from typing import Literal

from botocore.exceptions import ClientError
from enums.dynamo_filter import AttributeOperator
from enums.lambda_error import LambdaError
from enums.s3_lifecycle_tags import S3LifecycleTags
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import DocumentReference
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder
from utils.exceptions import DynamoServiceException
from utils.lambda_exceptions import DocumentDeletionServiceException

logger = LoggingService(__name__)


class DocumentDeletionService:
    def __init__(self):
        self.document_service = DocumentService()

    def handle_delete(
        self, nhs_number: str, doc_type: SupportedDocumentTypes
    ) -> list[DocumentReference]:
        files_deleted = []

        match doc_type:
            case SupportedDocumentTypes.ALL:
                arf_deleted = self.delete_specific_doc_type(
                    nhs_number, SupportedDocumentTypes.ARF
                )
                lg_deleted = self.delete_specific_doc_type(
                    nhs_number, SupportedDocumentTypes.LG
                )
                files_deleted = arf_deleted + lg_deleted
            case SupportedDocumentTypes.ARF | SupportedDocumentTypes.LG:
                files_deleted = self.delete_specific_doc_type(nhs_number, doc_type)

        return files_deleted

    def delete_specific_doc_type(
        self,
        nhs_number: str,
        doc_type: Literal[SupportedDocumentTypes.ARF, SupportedDocumentTypes.LG],
    ) -> list[DocumentReference]:
        try:
            filter_builder = DynamoQueryFilterBuilder()

            filter_expression = filter_builder.add_condition(
                "Deleted", AttributeOperator.EQUAL, ""
            ).build()
            results = self.document_service.fetch_available_document_references_by_type(
                nhs_number, doc_type, filter_expression
            )

            if not results:
                return []

            self.document_service.delete_documents(
                table_name=doc_type.get_dynamodb_table_name(),
                document_references=results,
                type_of_delete=str(S3LifecycleTags.SOFT_DELETE.value),
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
