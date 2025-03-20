import os
import re
import uuid
from datetime import datetime, timezone
from io import BytesIO

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.nrl_sqs_upload import NrlActionTypes
from enums.snomed_codes import SnomedCode, SnomedCodes
from enums.supported_document_types import SupportedDocumentTypes
from inflection import underscore
from models.document_reference import DocumentReference
from models.fhir.R4.nrl_fhir_document_reference import Attachment
from models.sqs.nrl_sqs_message import NrlSqsMessage
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
        self.target_dynamo_table = ""
        self.target_bucket = ""
        self.unstitched_lloyd_george_table_name = os.environ.get(
            "UNSTITCHED_LLOYD_GEORGE_DYNAMODB_NAME"
        )
        self.dynamo_service = DynamoDBService()
        self.s3_service = S3Service()
        self.document_service = DocumentService()
        self.sqs_service = SQSService()
        self.multipart_references: list[DocumentReference] = []
        self.stitched_reference: DocumentReference = None

    def retrieve_multipart_references(
        self, nhs_number: str, doc_type: SupportedDocumentTypes
    ) -> list[DocumentReference]:
        document_references = (
            self.document_service.fetch_available_document_references_by_type(
                nhs_number=nhs_number,
                doc_type=doc_type,
                query_filter=UploadCompleted,
            )
        )

        if doc_type == SupportedDocumentTypes.LG:
            if any("1of1" in result.file_name for result in document_references):
                logger.error(
                    "There is already a stitched LG document reference present in DynamoDb"
                )
                return []

        return document_references

    def process_message(self, stitching_message: PdfStitchingSqsMessage):
        doc_type = (
            SupportedDocumentTypes.LG
            if stitching_message.snomed_code_doc_type.code
            == SnomedCodes.LLOYD_GEORGE.value.code
            else SupportedDocumentTypes.ARF
        )

        if doc_type != SupportedDocumentTypes.LG:
            logger.info("Other document types have not been implemented yet")
            raise PdfStitchingException(400, LambdaError.StitchError)

        self.target_dynamo_table = doc_type.get_dynamodb_table_name()
        self.target_bucket = doc_type.get_s3_bucket_name()

        self.multipart_references = self.retrieve_multipart_references(
            nhs_number=stitching_message.nhs_number, doc_type=doc_type
        )

        if not self.multipart_references:
            logger.info("No usable files found for stitching")
            return

        try:
            self.create_stitched_reference(
                document_reference=self.multipart_references[0]
            )

            sorted_multipart_keys = self.sort_multipart_object_keys()
            stitching_data_stream = self.process_stitching(
                s3_object_keys=sorted_multipart_keys
            )

            self.upload_stitched_file(stitching_data_stream=stitching_data_stream)
            self.migrate_multipart_references()
            self.write_stitching_reference()
            self.publish_nrl_message(
                snomed_code_doc_type=stitching_message.snomed_code_doc_type
            )
        except Exception as e:
            self.rollback_stitching_process()
            raise e

    def create_stitched_reference(self, document_reference: DocumentReference):
        date_now = datetime.now(timezone.utc)
        reference_id = create_reference_id()
        stripped_filename = re.sub(r"^\d+of\d+_", "", document_reference.file_name)

        self.stitched_reference = DocumentReference(
            id=reference_id,
            content_type=document_reference.content_type,
            created=date_now.strftime(DATE_FORMAT),
            deleted="",
            file_location=f"s3://{self.target_bucket}/{document_reference.nhs_number}/{reference_id}",
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
            try:
                data_stream = BytesIO()
                self.s3_service.client.download_fileobj(
                    Bucket=self.target_bucket, Key=key, Fileobj=data_stream
                )
                data_stream.seek(0)

                pdf_reader = PdfReader(stream=data_stream)
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
            except ClientError as e:
                logger.error(f"Failed to retrieve stream data from S3: {e}")
                raise PdfStitchingException(400, LambdaError.StitchError)

        stitching_data_stream = BytesIO()
        pdf_writer.write(stream=stitching_data_stream)
        stitching_data_stream.seek(0)

        return stitching_data_stream

    def upload_stitched_file(self, stitching_data_stream: BytesIO):
        try:
            self.s3_service.client.upload_fileobj(
                Fileobj=stitching_data_stream,
                Bucket=self.target_bucket,
                Key=self.stitched_reference.get_file_key(),
            )
        except ClientError as e:
            logger.error(f"Failed to upload stitched file to S3: {e}")
            raise PdfStitchingException(400, LambdaError.StitchError)

    def migrate_multipart_references(self):
        logger.info("Migrating multipart references")
        try:
            for reference in self.multipart_references:
                migrated_item = reference.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude={
                        underscore(DocumentReferenceMetadataFields.CURRENT_GP_ODS.value)
                    },
                )
                self.dynamo_service.create_item(
                    table_name=self.unstitched_lloyd_george_table_name,
                    item=migrated_item,
                )
        except ClientError as e:
            logger.error(f"Failed to migrate multipart references: {e}")
            raise PdfStitchingException(400, LambdaError.MultipartError)

        try:
            for reference in self.multipart_references:
                self.dynamo_service.delete_item(
                    table_name=self.target_dynamo_table,
                    key={DocumentReferenceMetadataFields.ID.value: reference.id},
                )
        except ClientError as e:
            logger.error(f"Failed to cleanup multipart references: {e}")
            raise PdfStitchingException(400, LambdaError.MultipartError)

    def write_stitching_reference(self):
        try:
            self.dynamo_service.create_item(
                table_name=self.target_dynamo_table,
                item=self.stitched_reference.model_dump(
                    by_alias=True, exclude_none=True
                ),
            )
        except ClientError as e:
            logger.error(f"Failed to create stitching reference: {e}")
            raise PdfStitchingException(400, LambdaError.StitchError)

    def publish_nrl_message(self, snomed_code_doc_type: SnomedCode):
        document_api_endpoint = (
            os.environ.get("APIM_API_URL", "")
            + "/DocumentReference/"
            + snomed_code_doc_type.code
            + "~"
            + self.stitched_reference.id
        )
        doc_details = Attachment(
            url=document_api_endpoint,
            contentType="application/pdf",
        )
        nrl_sqs_message = NrlSqsMessage(
            nhs_number=self.stitched_reference.nhs_number,
            action=NrlActionTypes.CREATE,
            attachment=doc_details,
        )

        try:
            self.sqs_service.send_message_fifo(
                queue_url=os.environ.get("NRL_SQS_URL"),
                message_body=nrl_sqs_message.model_dump_json(),
                group_id=f"nrl_sqs_{uuid.uuid4()}",
            )
        except ClientError as e:
            logger.error(f"Failed to publish message onto NRL queue: {e}")
            raise PdfStitchingException(400, LambdaError.StitchError)

    def sort_multipart_object_keys(self) -> list[str]:
        try:
            self.multipart_references.sort(
                key=lambda x: int(re.search(r"(\d+)of(\d+)", x.file_name).group(1))
            )
        except AttributeError as e:
            logger.error(
                f"Failed to sort multipart file names from Patient's Document References: {e}"
            )
            raise PdfStitchingException(400, LambdaError.MultipartError)

        file_keys = [
            document_reference.get_file_key()
            for document_reference in self.multipart_references
        ]

        return file_keys

    def rollback_stitching_process(self):
        if self.stitched_reference:
            logger.info("Rolling back the following stitched reference and object")
            logger.info(self.stitched_reference.model_dump(by_alias=True))

        logger.info("Rolling back the following multipart references")
        for reference in self.multipart_references:
            logger.info(reference.model_dump_json(by_alias=True))

        self.rollback_stitched_reference()
        self.rollback_reference_migration()

        logger.info("Successfully completed stitching process rollback")

    def rollback_stitched_reference(self):
        try:
            if self.stitched_reference:
                self.dynamo_service.delete_item(
                    table_name=self.target_dynamo_table,
                    key={
                        DocumentReferenceMetadataFields.ID.value: self.stitched_reference.id
                    },
                )
                self.s3_service.delete_object(
                    s3_bucket_name=self.target_bucket,
                    file_key=self.stitched_reference.get_file_key(),
                )
                logger.info("Successfully reverted stitched object and reference")
        except Exception as e:
            logger.error(f"Failed to rollback newly stitched object and reference: {e}")
            raise PdfStitchingException(500, LambdaError.StitchRollbackError)

    def rollback_reference_migration(self):
        try:
            for document_reference in self.multipart_references:
                original_references = self.dynamo_service.get_item(
                    table_name=self.target_dynamo_table,
                    key={
                        DocumentReferenceMetadataFields.ID.value: document_reference.id
                    },
                )
                if not original_references.get("Item"):
                    logger.info("Reverting original multipart references deletion")
                    self.dynamo_service.create_item(
                        table_name=self.target_dynamo_table,
                        item=document_reference.model_dump(
                            by_alias=True, exclude_none=True
                        ),
                    )

                unstitched_references = self.dynamo_service.get_item(
                    table_name=self.unstitched_lloyd_george_table_name,
                    key={
                        DocumentReferenceMetadataFields.ID.value: document_reference.id
                    },
                )
                if unstitched_references.get("Item"):
                    logger.info("Reverting multipart references creation")
                    self.dynamo_service.delete_item(
                        table_name=self.unstitched_lloyd_george_table_name,
                        key={
                            DocumentReferenceMetadataFields.ID.value: document_reference.id
                        },
                    )
            logger.info("Successfully reverted migrated multipart references")

        except Exception as e:
            logger.error(f"Failed to rollback multipart migration process: {e}")
            raise PdfStitchingException(500, LambdaError.StitchRollbackError)
