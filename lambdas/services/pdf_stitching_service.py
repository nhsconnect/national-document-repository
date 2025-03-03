import os
import re
from datetime import datetime, timezone
from io import BytesIO

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage
from pypdf import PdfReader, PdfWriter
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service
from services.base.sqs_service import SQSService
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import UploadCompleted
from utils.lambda_exceptions import PdfStitchingException
from utils.utilities import DATE_FORMAT, create_reference_id

logger = LoggingService(__name__)


class PdfStitchingService:
    def __init__(self):
        self.lloyd_george_table_name = os.environ.get("LLOYD_GEORGE_DYNAMODB_NAME")
        self.unstitched_lloyd_george_table_name = os.environ.get(
            "UNSTITCHED_LLOYD_GEORGE_DYNAMODB_NAME"
        )
        self.lloyd_george_bucket_name = os.environ.get("LLOYD_GEORGE_BUCKET_NAME")
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()
        self.document_service = DocumentService()
        self.sqs_service = SQSService()
        self.stitched_reference: DocumentReference = None

    def process_message(self, stitching_message: PdfStitchingSqsMessage):
        document_references = (
            self.document_service.fetch_available_document_references_by_type(
                nhs_number=stitching_message.nhs_number,
                doc_type=SupportedDocumentTypes.LG,
                query_filter=UploadCompleted,
            )
        )
        if len(document_references) == 0 or "1of1" in [
            document_references.file_location
            for document_references in document_references
        ]:
            logger.info("No usable files found for stitching")
            raise PdfStitchingException(400, LambdaError.SqsInvalidEvent)

        self.create_stitched_reference(document_references[0])

        s3_object_keys = self.process_object_keys(document_references)
        stitching_data_stream = self.process_stitching(s3_object_keys=s3_object_keys)

        self.upload_stitched_file(stitching_data_stream)
        self.migrate_multipart_references(document_references)
        self.write_stitching_reference()
        self.publish_nrl_message()

    def create_stitched_reference(self, document_reference: DocumentReference):
        date_now = datetime.now(timezone.utc)
        reference_id = create_reference_id()
        stripped_filename = re.sub(r"^\d+of\d+_", "", document_reference.file_name)

        self.stitched_reference = DocumentReference(
            id=reference_id,
            content_type=document_reference.content_type,
            created=date_now.strftime(DATE_FORMAT),
            deleted="",
            file_location=f"s3://{self.lloyd_george_bucket_name}/{document_reference.nhs_number}/{reference_id}",
            file_name=f"1of1_{stripped_filename}",
            nhs_number=document_reference.nhs_number,
            virus_scanner_result=document_reference.virus_scanner_result,
            uploaded=document_reference.uploaded,
            uploading=document_reference.uploading,
            last_updated=int(date_now.timestamp()),
        )

    def process_stitching(self, s3_object_keys: list[str]) -> BytesIO:
        pdf_writer = PdfWriter()

        for key in s3_object_keys:
            data_stream = BytesIO()
            self.s3_service.client.download_fileobj(
                Bucket=self.lloyd_george_bucket_name, Key=key, Fileobj=data_stream
            )
            data_stream.seek(0)

            pdf_reader = PdfReader(data_stream)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

        stitching_data_stream = BytesIO()
        pdf_writer.write(stitching_data_stream)
        stitching_data_stream.seek(0)

        return stitching_data_stream

    def upload_stitched_file(self, stitching_data_stream: BytesIO):
        try:
            self.s3_service.client.upload_fileobj(
                Fileobj=stitching_data_stream,
                Bucket=self.lloyd_george_bucket_name,
                Key=self.stitched_reference.get_file_key(),
            )
        except ClientError as e:
            logger.error(f"Failed to upload stitched file to S3: {e}")
            raise PdfStitchingException(400, LambdaError.StitchError)

    def migrate_multipart_references(
        self, multipart_references: list[DocumentReference]
    ):
        for reference in multipart_references:
            try:
                self.dynamo_service.create_item(
                    table_name=self.unstitched_lloyd_george_table_name,
                    item=reference.model_dump_dynamo(),
                )
            except ClientError as e:
                logger.error(f"Failed to migrate multipart references: {e}")
                raise PdfStitchingException(400, LambdaError.MultipartError)

            try:
                self.dynamo_service.delete_item(
                    table_name=self.lloyd_george_table_name,
                    key={DocumentReferenceMetadataFields.ID: reference.id},
                )
            except ClientError as e:
                logger.error(f"Failed to cleanup multipart references: {e}")
                raise PdfStitchingException(400, LambdaError.MultipartError)

    def write_stitching_reference(self):
        try:
            self.dynamo_service.create_item(
                table_name=self.lloyd_george_table_name,
                item=self.stitched_reference.model_dump_dynamo(),
            )
        except ClientError as e:
            logger.error(f"Failed to create stitching reference: {e}")
            raise PdfStitchingException(400, LambdaError.StitchError)

    def publish_nrl_message(self):
        pass

    @staticmethod
    def process_object_keys(document_references: list[DocumentReference]) -> list[str]:
        try:
            document_references.sort(
                key=lambda x: int(re.search(r"(\d+)of(\d+)", x.file_name).group(1))
            )
        except AttributeError as e:
            logger.error(
                f"Failed to sort multipart file names from Patient's Document References: {e}"
            )
            raise PdfStitchingException(400, LambdaError.MultipartError)

        file_keys = [
            document_reference.get_file_key()
            for document_reference in document_references
        ]

        return file_keys
