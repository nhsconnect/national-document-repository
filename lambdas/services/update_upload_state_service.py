import os
from datetime import datetime, timezone

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
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
                if not doc_type or not doc_ref or not uploaded:
                    raise UpdateUploadStateException(
                        404, LambdaError.UpdateUploadStateValidation
                    )
                elif doc_type not in [
                    SupportedDocumentTypes.ARF.value,
                    SupportedDocumentTypes.LG.value,
                ]:
                    raise UpdateUploadStateException(
                        404, LambdaError.UpdateUploadStateDocType
                    )
                else:
                    self.update_document(doc_ref, doc_type, uploaded)
        except (KeyError, TypeError) as e:
            logger.error(
                f"{LambdaError.UpdateUploadStateKey.to_str()} :{str(e)}",
            )
            raise UpdateUploadStateException(404, LambdaError.UpdateUploadStateKey)

    def update_document(self, doc_ref, doc_type, uploaded):
        updated_fields = self.format_update({Fields.UPLOADING.value: uploaded})
        table = (
            self.lg_dynamo_table
            if doc_type == SupportedDocumentTypes.LG.value
            else self.arf_dynamo_table
        )
        try:
            self.dynamo_service.update_item(
                table_name=table,
                key=doc_ref,
                updated_fields=updated_fields,
            )
        except ClientError as e:
            logger.error(
                f"{LambdaError.UpdateUploadStateClient.to_str()} :{str(e)}",
            )
            raise UpdateUploadStateException(500, LambdaError.UpdateUploadStateClient)

    def format_update(self, fields):
        try:
            date_now = int(datetime.now(timezone.utc).timestamp())
            return {**fields, Fields.LAST_UPDATED.value: date_now}
        except TypeError as e:
            logger.error(
                f"{LambdaError.UpdateUploadStateFieldType.to_str()} :{str(e)}",
            )
            raise UpdateUploadStateException(
                404, LambdaError.UpdateUploadStateFieldType
            )
