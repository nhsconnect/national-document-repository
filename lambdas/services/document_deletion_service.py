import os
import uuid
from typing import Literal
from urllib.parse import urlparse

from botocore.exceptions import ClientError
from enums.document_retention import DocumentRetentionDays
from enums.lambda_error import LambdaError
from enums.nrl_sqs_upload import NrlActionTypes
from enums.snomed_codes import SnomedCodesCategory, SnomedCodesType
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from models.nrl_sqs_message import NrlSqsMessage
from services.base.sqs_service import SQSService
from services.document_service import DocumentService
from services.lloyd_george_stitch_job_service import LloydGeorgeStitchJobService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import NotDeleted
from utils.exceptions import DocumentServiceException, DynamoServiceException
from utils.lambda_exceptions import DocumentDeletionServiceException

logger = LoggingService(__name__)


class DocumentDeletionService:
    def __init__(self):
        self.document_service = DocumentService()
        self.stitch_service = LloydGeorgeStitchJobService()
        self.sqs_service = SQSService()

    def handle_reference_delete(
        self, nhs_number: str, doc_types: list[SupportedDocumentTypes]
    ) -> list[DocumentReference]:
        files_deleted = []
        for doc_type in doc_types:
            files_deleted += self.delete_specific_doc_type(nhs_number, doc_type)
        self.delete_documents_references_in_stitch_table(nhs_number)
        if SupportedDocumentTypes.LG in doc_types:
            self.send_sqs_message_to_remove_pointer(nhs_number)
        return files_deleted

    def handle_object_delete(self, deleted_reference: DocumentReference):
        try:
            s3_uri = deleted_reference.file_location

            parsed_uri = urlparse(s3_uri)
            bucket_name = parsed_uri.netloc
            object_key = parsed_uri.path.lstrip("/")

            if not bucket_name or not object_key:
                raise DocumentDeletionServiceException(
                    400, LambdaError.DocDelObjectFailure
                )

            self.document_service.delete_document_object(
                bucket=bucket_name, key=object_key
            )

            logger.info(
                "Successfully deleted Document Reference S3 Object",
                {"Result": "Successful deletion"},
            )
        except DocumentServiceException as e:
            logger.error(
                str(e),
                {"Results": "Failed to delete document"},
            )
            raise DocumentDeletionServiceException(400, LambdaError.DocDelObjectFailure)

    def get_documents_references_in_storage(
        self,
        nhs_number: str,
        doc_type: Literal[SupportedDocumentTypes.ARF, SupportedDocumentTypes.LG],
    ) -> list[DocumentReference]:
        results = self.document_service.fetch_available_document_references_by_type(
            nhs_number, doc_type, NotDeleted
        )
        return results

    def delete_documents_references_in_stitch_table(self, nhs_number: str):
        documents_in_stitch_table = (
            self.stitch_service.query_stitch_trace_with_nhs_number(nhs_number) or []
        )

        for record in documents_in_stitch_table:
            record.deleted = True
            self.document_service.dynamo_service.update_item(
                self.stitch_service.stitch_trace_table,
                record.id,
                record.model_dump(by_alias=True, include={"deleted"}),
            )

    def delete_specific_doc_type(
        self,
        nhs_number: str,
        doc_type: Literal[SupportedDocumentTypes.ARF, SupportedDocumentTypes.LG],
    ) -> list[DocumentReference]:
        try:
            results = self.get_documents_references_in_storage(nhs_number, doc_type)
            if results:
                self.document_service.delete_document_references(
                    table_name=doc_type.get_dynamodb_table_name(),
                    document_references=results,
                    document_ttl_days=DocumentRetentionDays.SOFT_DELETE,
                )

            logger.info(
                f"Deleted document of type {doc_type.value}",
                {"Result": "Successful deletion"},
            )
            return results
        except (ClientError, DynamoServiceException) as e:
            logger.error(
                f"{LambdaError.DocDelClient.to_str()}: {str(e)}",
                {"Results": "Failed to delete documents"},
            )
            raise DocumentDeletionServiceException(500, LambdaError.DocDelClient)

    def send_sqs_message_to_remove_pointer(self, nhs_number: str):
        delete_nrl_message = NrlSqsMessage(
            nhs_number=nhs_number,
            action=NrlActionTypes.DELETE,
            snomed_code_doc_type=SnomedCodesType.LLOYD_GEORGE,
            snomed_code_category=SnomedCodesCategory.CARE_PLAN,
        )
        sqs_group_id = f"NRL_delete_{uuid.uuid4()}"
        nrl_queue_url = os.environ["NRL_SQS_QUEUE_URL"]
        self.sqs_service.send_message_fifo(
            queue_url=nrl_queue_url,
            message_body=delete_nrl_message.model_dump_json(),
            group_id=sqs_group_id,
        )
