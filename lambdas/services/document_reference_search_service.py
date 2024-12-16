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
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder
from utils.exceptions import DynamoServiceException
from utils.lambda_exceptions import DocumentRefSearchException

logger = LoggingService(__name__)


class DocumentReferenceSearchService(DocumentService):
    def get_document_references(self, nhs_number: str):
        try:
            list_of_table_names = json.loads(os.environ["DYNAMODB_TABLE_LIST"])
            results: list[dict] = []

            filter_builder = DynamoQueryFilterBuilder()
            delete_filter_expression = filter_builder.add_condition(
                attribute=str(DocumentReferenceMetadataFields.DELETED.value),
                attr_operator=AttributeOperator.EQUAL,
                filter_value="",
            ).build()

            for table_name in list_of_table_names:
                logger.info(f"Searching for results in {table_name}")

                documents: list[DocumentReference] = (
                    self.fetch_documents_from_table_with_filter(
                        nhs_number,
                        table_name,
                        query_filter=delete_filter_expression,
                    )
                )
                if self.is_upload_in_process(documents):
                    logger.error(
                        "Records are in the process of being uploaded. Will not process the new upload.",
                        {"Result": "Document reference search failed"},
                    )
                    raise DocumentRefSearchException(
                        423, LambdaError.UploadInProgressError
                    )
                results.extend(
                    {
                        **document.model_dump(
                            include={
                                "file_name",
                                "created",
                                "virus_scanner_result",
                                "id",
                            },
                            by_alias=True,
                        ),
                        "fileSize": self.s3_service.get_file_size(
                            bucket_name=document.get_file_bucket(),
                            object_key=document.get_file_key(),
                        ),
                    }
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
