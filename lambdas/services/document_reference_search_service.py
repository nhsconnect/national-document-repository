import json
import os
from json import JSONDecodeError

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from models.document_reference import DocumentReference
from pydantic import ValidationError
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.common_query_filters import NotDeleted
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
                documents: list[DocumentReference] = (
                    self.fetch_documents_from_table_with_nhs_number(
                        nhs_number,
                        table_name,
                        query_filter=NotDeleted,
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
                for document in documents:
                    document_formatted = document.model_dump_camel_case(
                        exclude_none=True,
                        include={
                            "id",
                            "file_name",
                            "created",
                            "virus_scanner_result",
                            "size",
                        },
                    )
                    if not document.size:
                        document_formatted.update(
                            {
                                "fileSize": self.s3_service.get_file_size(
                                    s3_bucket_name=document.s3_bucket_name,
                                    object_key=document.s3_file_key,
                                ),
                            }
                        )
                    results.append(document_formatted)
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
