import os
import shutil
import tempfile
import zipfile
from typing import Dict

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from models.document_reference import DocumentReference
from models.zip_trace import ZipTrace
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import (
    DocumentManifestServiceException,
    GenerateManifestZipException,
)

logger = LoggingService(__name__)


class DocumentZipService:
    def __init__(self):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()
        self.temp_output_dir = tempfile.mkdtemp()
        self.temp_downloads_dir = tempfile.mkdtemp()
        self.zip_file_name = "patient-record-{}.zip"
        self.zip_trace_object = None
        self.zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        self.zip_trace_table = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]
        self.zip_file_path = os.path.join(self.temp_output_dir, self.zip_file_name)
        self.file_names_to_be_zipped = {}

    def handle_zip_request(self, job_id: str):
        self.arrange_zip_trace_object(job_id)
        # self.download_documents_to_be_zipped(documents)
        self.upload_zip_file()
        self.remove_temp_files()

    def download_documents_to_be_zipped(self, documents: list[DocumentReference]):
        logger.info("Downloading documents to be zipped")

        for document in documents:
            self.handle_duplication_in_filename(document)
            self.download_file(document)

    def download_file(self, document):
        download_path = os.path.join(self.temp_downloads_dir, document.file_name)

        try:
            self.s3_service.download_file(
                document.get_file_bucket(), document.get_file_key(), download_path
            )
        except ClientError as e:
            msg = f"{document.get_file_key()} may reference missing file in s3 bucket: {document.get_file_bucket()}"
            logger.error(
                f"{LambdaError.ManifestClient.to_str()} {msg + str(e)}",
                {"Result": "Failed to create document manifest"},
            )
            raise DocumentManifestServiceException(
                status_code=500, error=LambdaError.ManifestClient
            )

    def handle_duplication_in_filename(self, document):
        duplicated_filename = document.file_name in self.file_names_to_be_zipped

        if duplicated_filename:
            self.file_names_to_be_zipped[document.file_name] += 1
            document.file_name = document.create_unique_filename(
                self.file_names_to_be_zipped[document.file_name]
            )

        else:
            self.file_names_to_be_zipped[document.file_name] = 1

    def upload_zip_file(self):
        logger.info("Uploading zip file to s3")
        self.s3_service.upload_file(
            file_name=self.zip_file_path,
            s3_bucket_name=self.zip_output_bucket,
            file_key=f"{self.zip_file_name}",
        )

    def zip_file(self):
        logger.info("Creating zip from files")
        with zipfile.ZipFile(self.zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.temp_downloads_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, self.temp_downloads_dir)
                    zipf.write(file_path, arc_name)

    def update_dynamo_with_zip_location(self, zip_trace: ZipTrace):
        logger.info("Writing zip trace to db")
        zip_trace.zip_file_location = (
            f"s3://{self.zip_output_bucket}/{self.zip_file_name}",
        )
        self.dynamo_service.create_item(
            self.zip_trace_table, zip_trace.model_dump(by_alias=True)
        )

    def remove_temp_files(self):
        # Removes the parent of each removed directory until the parent does not exist or the parent is not empty
        shutil.rmtree(self.temp_downloads_dir)
        shutil.rmtree(self.temp_output_dir)

    def arrange_zip_trace_object(self, job_id):
        dynamo_response = self.get_zip_trace_item_from_dynamo_by_job_id(job_id)
        dynamo_item = self.extract_item_from_dynamo_response(dynamo_response)
        self.checking_number_of_items_is_one(dynamo_item)
        self.zip_trace_object = self.create_zip_trace_object(dynamo_item)

    def get_zip_trace_item_from_dynamo_by_job_id(self, job_id):
        try:
            return self.dynamo_service.query_with_requested_fields(
                table_name=self.zip_trace_table,
                index_name="JobIdIndex",
                search_key="JobId",
                search_condition=job_id,
            )
        except ClientError:
            logger.error("Failed querying Dynamo with job id")
            raise GenerateManifestZipException(
                status_code=500, error=LambdaError.FailedToQueryDynamo
            )

    @staticmethod
    def extract_item_from_dynamo_response(dynamo_response) -> Dict:
        try:
            return dynamo_response["Items"]
        except KeyError:
            raise GenerateManifestZipException(
                status_code=500, error=LambdaError.FailedToQueryDynamo
            )

    @staticmethod
    def checking_number_of_items_is_one(items) -> None:
        if len(items) > 1:
            raise GenerateManifestZipException(
                status_code=400, error=LambdaError.DuplicateJobId
            )

        elif len(items) == 0:
            raise GenerateManifestZipException(
                status_code=404, error=LambdaError.JobIdNotFound
            )

    @staticmethod
    def create_zip_trace_object(dynamodb_item):
        try:
            return ZipTrace.model_validate(dynamodb_item)

        except ValidationError as e:
            logger.error(
                f"{LambdaError.ManifestValidation.to_str()}: {str(e)}",
                {"Result": "Failed to create document manifest"},
            )
            raise DocumentManifestServiceException(
                status_code=500, error=LambdaError.ManifestValidation
            )
