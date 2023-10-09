from datetime import datetime, timezone
from typing import Any

from enums.metadata_field_names import DocumentReferenceMetadataFields
from pydantic import BaseModel, model_validator

from services.lloyd_george_validator import validate_lg_file_type


class UploadRequestDocument(BaseModel):
    fileName: str
    contentType: str
    docType: str

    @model_validator(mode='before')
    @classmethod
    def check_file_type_for_lg(cls, data: Any) -> Any:
        if isinstance(data, dict):
            doc_type = data.get('docType')
            content_type = data.get('contentType')
        elif isinstance(data, UploadRequestDocument):
            doc_type = data.docType
            content_type = data.contentType
        if doc_type == 'LG':
            validate_lg_file_type(content_type)
        return data


class NHSDocumentReference:
    def __init__(
        self, nhs_number, content_type, file_name, reference_id, s3_bucket_name
    ) -> None:
        self.id = reference_id
        self.nhs_number = nhs_number
        self.content_type = content_type
        self.file_name = file_name
        self.created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.s3_bucket_name = s3_bucket_name
        self.deleted = None
        self.uploaded = None
        self.virus_scanner_result = "Not Scanned"
        self.file_location = f"s3://{self.s3_bucket_name}/{self.nhs_number}/{self.id}"

    def set_uploaded(self) -> None:
        self.uploaded = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def set_deleted(self) -> None:
        self.deleted = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def set_virus_scanner_result(self, updated_virus_scanner_result) -> None:
        self.virus_scanner_result = updated_virus_scanner_result

    def update_location(self, updated_file_location):
        self.file_location = updated_file_location

    def is_uploaded(self) -> bool:
        return bool(self.uploaded)

    def to_dict(self):
        document_metadata = {
            DocumentReferenceMetadataFields.ID.field_name: str(self.id),
            DocumentReferenceMetadataFields.NHS_NUMBER.field_name: self.nhs_number,
            DocumentReferenceMetadataFields.FILE_NAME.field_name: self.file_name,
            DocumentReferenceMetadataFields.FILE_LOCATION.field_name: self.file_location,
            DocumentReferenceMetadataFields.CREATED.field_name: self.created,
            DocumentReferenceMetadataFields.CONTENT_TYPE.field_name: self.content_type,
            DocumentReferenceMetadataFields.VIRUS_SCAN_RESULT.field_name: self.virus_scanner_result,
        }
        return document_metadata

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.nhs_number == other.nhs_number
            and self.content_type == other.content_type
            and self.file_name == other.file_name
            and self.created == other.created
            and self.deleted == other.deleted
            and self.uploaded == other.uploaded
            and self.virus_scanner_result == other.virus_scan_result
            and self.file_location == other.file_location
        )
