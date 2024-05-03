from datetime import datetime, timezone

from botocore.exceptions import ClientError
from enums.lambda_error import LambdaError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from models.document_reference import UploadDocumentReferences
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

    def handle_update_state(self, event_body: dict):
        try:
            upload_document_references = UploadDocumentReferences.model_validate(
                event_body
            )

            for file in upload_document_references.files:
                self.update_document(
                    file.reference,
                    file.doc_type,
                    file.fields[str(Fields.UPLOADING.value)],
                )
        except (KeyError, TypeError) as e:
            logger.error(
                f"{LambdaError.UpdateUploadStateKey.to_str()} :{str(e)}",
            )
            raise UpdateUploadStateException(400, LambdaError.UpdateUploadStateKey)
        except ValidationError as e:
            logger.error(
                f"{LambdaError.UpdateUploadStateValidation.to_str()} :{str(e)}",
            )
            raise UpdateUploadStateException(
                400, LambdaError.UpdateUploadStateValidation
            )

    def update_document(
        self, doc_ref: str, doc_type: SupportedDocumentTypes, uploaded: bool
    ):
        updated_fields = self.format_update({Fields.UPLOADING.value: uploaded})
        table = doc_type.get_dynamodb_table_name()
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

    def format_update(self, fields: dict) -> dict:
        try:
            date_now = int(datetime.now(timezone.utc).timestamp())
            return {**fields, Fields.LAST_UPDATED.value: date_now}
        except TypeError as e:
            logger.error(
                f"{LambdaError.UpdateUploadStateFieldType.to_str()} :{str(e)}",
            )
            raise UpdateUploadStateException(
                400, LambdaError.UpdateUploadStateFieldType
            )
