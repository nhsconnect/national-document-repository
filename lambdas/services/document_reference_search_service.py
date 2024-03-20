import json
import os
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.dynamo_filter import AttributeOperator
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.document_reference import DocumentReference
from pydantic import ValidationError
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.dynamo_utils import DynamoQueryFilterBuilder
from utils.exceptions import DynamoServiceException
from utils.lambda_exceptions import DocumentRefSearchException

logger = LoggingService(__name__)


class DocumentReferenceSearchService(DocumentService):
    def get_document_references(self, nhs_number: str):
        try:
            list_of_table_names = json.loads(os.environ["DYNAMODB_TABLE_LIST"])

            results: list[dict] = []

            filter_builder = DynamoQueryFilterBuilder()

            filter_builder.add_condition(
                attribute=str(DocumentReferenceMetadataFields.DELETED.value),
                attr_operator=AttributeOperator.EQUAL,
                filter_value="",
            )

            delete_filter_expression = filter_builder.build()

            for table_name in list_of_table_names:
                logger.info(f"Searching for results in {table_name}")

                documents: list[
                    DocumentReference
                ] = self.fetch_documents_from_table_with_filter(
                    nhs_number,
                    table_name,
                    query_filter=delete_filter_expression,
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
                f"{LambdaError.DocRefClient.to_str()}: {str(e)}",
                {"Result": "Document reference search failed"},
            )
            raise DocumentRefSearchException(500, LambdaError.DocRefClient)
