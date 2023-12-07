import os
import shutil
import tempfile
import zipfile

from botocore.exceptions import ClientError
from models.document_reference import DocumentReference
from models.zip_trace import ZipTrace
from pydantic import ValidationError
from services.document_service import DocumentService
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.exceptions import (DocumentManifestServiceException,
                              DynamoDbException)

logger = LoggingService(__name__)


class DocumentManifestService:
    def __init__(self, nhs_number):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()
        self.document_service = DocumentService()

        self.nhs_number = nhs_number
        self.documents: list[DocumentReference] = []
        self.zip_file_name = f"patient-record-{self.nhs_number}.zip"
        self.temp_downloads_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()
        self.zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        self.zip_trace_table = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]
        # TODO - Add time to live for zipped manifest
        # zip_trace_ttl = os.environ["DOCUMENT_ZIP_TRACE_TTL_IN_DAYS"]

    def create_document_manifest_presigned_url(self, doc_type: str) -> str:
        try:
            self.documents = (
                self.document_service.fetch_available_document_references_by_type(
                    self.nhs_number, doc_type
                )
            )
            if not self.documents:
                raise DocumentManifestServiceException(
                    status_code=404,
                    message="No documents found for given NHS number and document type",
                )
        except ValidationError:
            raise DocumentManifestServiceException(
                status_code=500,
                message="Failed to parse document reference from from DynamoDb response",
            )
        except DynamoDbException as e:
            raise DocumentManifestServiceException(
                status_code=500,
                message=str(e),
            )

        self.download_documents_to_be_zipped()
        self.upload_zip_file()

        shutil.rmtree(self.temp_downloads_dir)
        shutil.rmtree(self.temp_output_dir)

        return self.s3_service.create_download_presigned_url(
            s3_bucket_name=self.zip_output_bucket, file_key=self.zip_file_name
        )

    def download_documents_to_be_zipped(self):
        logger.info("Downloading documents to be zipped")
        file_names_to_be_zipped = {}

        for document in self.documents:
            file_name = document.file_name

            duplicated_filename = file_name in file_names_to_be_zipped

            if duplicated_filename:
                file_names_to_be_zipped[file_name] += 1
                document.file_name = document.create_unique_filename(
                    file_names_to_be_zipped[file_name]
                )

            else:
                file_names_to_be_zipped[file_name] = 1

            download_path = os.path.join(self.temp_downloads_dir, document.file_name)

            try:
                self.s3_service.download_file(
                    document.get_file_bucket(), document.get_file_key(), download_path
                )
            except ClientError:
                raise DocumentManifestServiceException(
                    status_code=500,
                    message=f"Reference to {document.file_key} that doesn't exist in s3",
                )

    def upload_zip_file(self):
        logger.info("Creating zip from files")
        temp_output_dir = tempfile.mkdtemp()

        zip_file_path = os.path.join(temp_output_dir, self.zip_file_name)
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.temp_downloads_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, self.temp_downloads_dir)
                    zipf.write(file_path, arc_name)

        logger.info("Uploading zip file to s3")
        self.s3_service.upload_file(
            file_name=zip_file_path,
            s3_bucket_name=self.zip_output_bucket,
            file_key=f"{self.zip_file_name}",
        )

        logger.info("Writing zip trace to db")
        zip_trace = ZipTrace(
            f"s3://{self.zip_output_bucket}/{self.zip_file_name}",
        )

        self.dynamo_service.create_item(self.zip_trace_table, zip_trace.to_dict())
