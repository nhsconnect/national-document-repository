import io
import os
import shutil
import zipfile

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.trace_status import TraceStatus
from models.zip_trace import DocumentManifestZipTrace
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from utils.audit_logging_setup import LoggingService
from utils.exceptions import InvalidDocumentReferenceException
from utils.lambda_exceptions import GenerateManifestZipException

logger = LoggingService(__name__)


class DocumentManifestZipService:
    def __init__(self, zip_trace: DocumentManifestZipTrace):
        self.s3_service = S3Service()
        self.dynamo_service = DynamoDBService()
        self.zip_trace_object = zip_trace
        self.zip_output_bucket = os.environ["ZIPPED_STORE_BUCKET_NAME"]
        self.zip_trace_table = os.environ["ZIPPED_STORE_DYNAMODB_NAME"]
        self.zip_file_name = f"patient-record-{zip_trace.job_id}.zip"

    def handle_zip_request(self):
        self.update_status(TraceStatus.PROCESSING)
        zip_buffer = self.stream_zip_documents()
        self.upload_zip_file(zip_buffer)
        self.update_dynamo_with_fields({"job_status", "zip_file_location"})

    def stream_zip_documents(self) -> io.BytesIO:
        logger.info("Streaming and zipping documents in-memory")
        documents = self.zip_trace_object.files_to_download  # Dict[str, str]

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for document_location, document_name in documents.items():
                file_bucket, file_key = self.get_file_bucket_and_key(document_location)
                try:
                    # Stream file from S3
                    s3_object_stream = self.s3_service.get_object_stream(
                        file_bucket, file_key
                    )
                    with zipf.open(document_name, mode="w") as zip_member:
                        shutil.copyfileobj(
                            s3_object_stream, zip_member, length=64 * 1024
                        )
                except ClientError as e:
                    # self.update_failed_status()
                    self.update_status(TraceStatus.FAILED)
                    msg = f"Failed to fetch S3 object {file_bucket}/{file_key}: {e}"
                    logger.error(f"{LambdaError.ZipServiceClientError.to_str()} {msg}")
                    raise GenerateManifestZipException(
                        status_code=500, error=LambdaError.ZipServiceClientError
                    )
        zip_buffer.seek(0)
        return zip_buffer

    def get_file_bucket_and_key(self, file_location: str):
        try:
            file_bucket, file_key = file_location.replace("s3://", "").split("/", 1)
            return file_bucket, file_key
        except ValueError:
            self.update_status(TraceStatus.FAILED)
            raise InvalidDocumentReferenceException(
                "Failed to parse bucket from file location string"
            )

    def upload_zip_file(self, zip_buffer: io.BytesIO):
        logger.info("Uploading zip file to s3")
        zip_file_key = f"{self.zip_file_name}"
        self.zip_trace_object.zip_file_location = (
            f"s3://{self.zip_output_bucket}/{zip_file_key}"
        )
        try:
            self.s3_service.upload_file_obj(
                zip_buffer, self.zip_output_bucket, zip_file_key
            )
            logger.info(
                f"Successfully uploaded ZIP file to S3: s3://{self.zip_output_bucket}/{zip_file_key}"
            )

        except ClientError as e:
            self.update_status(TraceStatus.FAILED)
            logger.error(e, {"Result": "Failed to create document manifest"})
            raise GenerateManifestZipException(
                status_code=500, error=LambdaError.ZipServiceClientError
            )

        self.zip_trace_object.job_status = TraceStatus.COMPLETED

    def update_dynamo_with_fields(self, fields: set):
        logger.info("Writing zip trace to db")
        self.dynamo_service.update_item(
            table_name=self.zip_trace_table,
            key_pair={"ID": self.zip_trace_object.id},
            updated_fields=self.zip_trace_object.model_dump(
                by_alias=True, include=fields
            ),
        )

    def update_status(self, job_status: TraceStatus):
        self.zip_trace_object.job_status = job_status
        self.update_dynamo_with_fields({"job_status"})
