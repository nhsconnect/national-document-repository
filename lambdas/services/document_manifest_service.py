import logging
import os
import shutil
import tempfile
import zipfile

from botocore.exceptions import ClientError
from models.document import Document
from models.zip_trace import ZipTrace
from services.dynamo_service import DynamoDBService
from services.s3_service import S3Service
from utils.exceptions import ManifestDownloadException

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DocumentManifestService:
    def __init__(
        self,
        nhs_number: str,
        documents: list[Document],
        zip_output_bucket: str,
        zip_trace_table: str,
    ):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()
        self.nhs_number = nhs_number
        self.documents = documents
        self.zip_output_bucket = zip_output_bucket
        self.zip_trace_table = zip_trace_table
        self.zip_file_name = f"patient-record-{self.nhs_number}.zip"
        self.temp_downloads_dir = tempfile.mkdtemp()
        self.temp_output_dir = tempfile.mkdtemp()

    def create_document_manifest_presigned_url(self) -> str:
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
                    document.file_bucket, document.file_key, download_path
                )
            except ClientError:
                logger.error(
                    f"{document.file_key} may reference missing file in s3 bucket {document.file_bucket}"
                )
                raise ManifestDownloadException(
                    f"Reference to {document.file_key} that doesn't exist in s3"
                )

    def upload_zip_file(self):
        logger.info("Creating zip from files")
        temp_output_dir = tempfile.mkdtemp()

        zip_file_path = os.path.join(temp_output_dir, self.zip_file_name)
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.temp_downloads_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.temp_downloads_dir)
                    zipf.write(file_path, arcname)

        logger.info("Uploading zip file to s3")
        self.s3_service.upload_file(
            file_name=zip_file_path,
            s3_bucket_name=self.zip_output_bucket,
            file_key=f"{self.zip_file_name}",
        )

        logger.info("Writing zip trace to db")
        zip_trace = ZipTrace(
            self.zip_file_name,
            f"s3://{self.zip_output_bucket}/{self.zip_file_name}",
        )

        self.dynamo_service.create_item(self.zip_trace_table, zip_trace.to_dict())
