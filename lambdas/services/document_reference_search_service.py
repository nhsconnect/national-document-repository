import json
import os
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.document_reference import DocumentReference
from pydantic import ValidationError
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import DynamoServiceException
from utils.lambda_exceptions import DocumentRefSearchException

logger = LoggingService(__name__)


class DocumentReferenceSearchService(DocumentService):
    def get_document_references(self, nhs_number: str):
        try:
            list_of_table_names = json.loads(os.environ["DYNAMODB_TABLE_LIST"])

            results: list[dict] = []
            for table_name in list_of_table_names:
                logger.info(f"Searching for results in {table_name}")
                documents: list[
                    DocumentReference
                ] = self.fetch_documents_from_table_with_filter(
                    nhs_number,
                    table_name,
                    attr_filter={DocumentReferenceMetadataFields.DELETED.value: ""},
                )

                results.extend(
                    document.model_dump(
                        include={"file_name", "created", "virus_scanner_result"},
                        by_alias=True,
                    )
                    for document in documents
                )
            return results
        except (
            JSONDecodeError,
            ValidationError,
            ClientError,
            DynamoServiceException,
        ) as e:
            logger.error(
                f"An error occurred when using document reference search service: {str(e)}",
            )
            raise DocumentRefSearchException(
                500, "An error occurred when searching for available documents"
            )
