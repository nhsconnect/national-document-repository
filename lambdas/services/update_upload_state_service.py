import os
from datetime import datetime, timezone

from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from pydantic import ValidationError
from services.base.dynamo_service import DynamoDBService
from utils.audit_logging_setup import LoggingService
from utils.lambda_exceptions import UpdateUploadStateException

logger = LoggingService(__name__)
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
FAILED_FIELDS_ERROR = "Validation error on files and fields"
Fields = DocumentReferenceMetadataFields


class UpdateUploadStateService:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.lg_dynamo_table = os.getenv("LLOYD_GEORGE_DYNAMODB_NAME")
        self.arf_dynamo_table = os.getenv("DOCUMENT_STORE_DYNAMODB_NAME")

    def handle_update_state(self, event_body):
        try:
            files = event_body["files"]
            for file in files:
                doc_ref = file["reference"]
                doc_type = file["type"]
                uploaded = file["fields"][Fields.UPLOADING.value]
                self.update_document(
                    doc_ref=doc_ref, doc_type=doc_type, uploaded=uploaded["value"]
                )
        except (ValidationError, KeyError, TypeError) as e:
            logger.error(
                f"{LambdaError.UpdateUploadStateValidation.to_str()} :{str(e)}",
            )
            raise UpdateUploadStateException(
                400, LambdaError.UpdateUploadStateValidation
            )

    def update_document(self, doc_ref, doc_type, uploaded):
        table = self.arf_dynamo_table if doc_type == "ARF" else self.lg_dynamo_table
        updated_fields = {Fields.UPLOADING.value: uploaded}
        self.dynamo_service.update_item(
            table_name=table,
            key=doc_ref,
            updated_fields=self.format_status_update(updated_fields),
        )

    def format_update(self, fields):
        date_now = int(datetime.now(timezone.utc).timestamp())
        return {**fields, Fields.LAST_UPDATED.value: date_now}
