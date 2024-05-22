import pathlib
from datetime import datetime, timezone
from typing import Optional

from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from pydantic import BaseModel, Field
from utils.exceptions import InvalidDocumentReferenceException


class UploadDocumentReference(BaseModel):
    reference: str = Field(...)
    doc_type: SupportedDocumentTypes = Field(..., alias="type")
    fields: dict[str, bool] = Field(...)


class UploadDocumentReferences(BaseModel):
    files: list[UploadDocumentReference] = Field(...)


class DocumentReference(BaseModel):
    id: str = Field(..., alias=str(DocumentReferenceMetadataFields.ID.value))
    content_type: str = Field(
        ..., alias=str(DocumentReferenceMetadataFields.CONTENT_TYPE.value)
    )
    created: str = Field(
        ...,
        alias=str(DocumentReferenceMetadataFields.CREATED.value),
        serialization_alias="created",
    )
    deleted: str = Field(..., alias=str(DocumentReferenceMetadataFields.DELETED.value))
    file_location: str = Field(
        ..., alias=str(DocumentReferenceMetadataFields.FILE_LOCATION.value)
    )
    file_name: str = Field(
        ...,
        alias=str(DocumentReferenceMetadataFields.FILE_NAME.value),
        serialization_alias="fileName",
    )
    nhs_number: str = Field(
        ..., alias=str(DocumentReferenceMetadataFields.NHS_NUMBER.value)
    )
    ttl: Optional[int] = Field(
        alias=str(DocumentReferenceMetadataFields.TTL.value), default=None
    )
    virus_scanner_result: str = Field(
        ...,
        alias=str(DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT.value),
        serialization_alias="virusScannerResult",
    )
    # Allow current_gp_ods to be nullable so that we can cope with existing records.
    # After we updated all existing records with this field, consider to set this as non-Optional
    current_gp_ods: Optional[str] = Field(
        alias=str(DocumentReferenceMetadataFields.CURRENT_GP_ODS.value), default=None
    )

    uploaded: bool = Field(alias=str(DocumentReferenceMetadataFields.UPLOADED.value))
    uploading: bool = Field(alias=str(DocumentReferenceMetadataFields.UPLOADING.value))
    last_updated: int = Field(
        alias=str(DocumentReferenceMetadataFields.LAST_UPDATED.value),
        serialization_alias="lastUpdated",
    )

    def get_file_name_path(self):
        return pathlib.Path(self.file_name)

    def get_base_name(self):
        return self.get_file_name_path().stem

    def get_file_extension(self):
        return self.get_file_name_path().suffix

    def get_file_bucket(self):
        try:
            file_bucket = self.file_location.replace("s3://", "").split("/")[0]
            if file_bucket:
                return file_bucket
            raise InvalidDocumentReferenceException(
                "Failed to parse bucket from file location"
            )
        except IndexError:
            raise InvalidDocumentReferenceException(
                "Failed to parse bucket from file location"
            )

    def get_file_key(self):
        try:
            file_key = self.file_location.replace("s3://", "").split("/", 1)[1]
            if file_key:
                return file_key
            raise InvalidDocumentReferenceException(
                "Failed to parse object key from file location"
            )
        except IndexError:
            raise InvalidDocumentReferenceException(
                "Failed to parse object key from file location"
            )

    def create_unique_filename(self, duplicates: int):
        return f"{self.get_base_name()}({duplicates}){self.get_file_extension()}"

    def last_updated_within_three_minutes(self) -> bool:
        three_minutes_ago = datetime.now(timezone.utc).timestamp() - 60 * 3
        return self.last_updated >= three_minutes_ago

    def __eq__(self, other):
        if isinstance(other, DocumentReference):
            return (
                self.id == other.id
                and self.content_type == other.content_type
                and self.created == other.created
                and self.deleted == other.deleted
                and self.file_location == other.file_location
                and self.file_name == other.file_name
                and self.nhs_number == other.nhs_number
                and self.ttl == other.ttl
                and self.virus_scanner_result == other.virus_scanner_result
                and self.current_gp_ods == other.current_gp_ods
                and self.uploaded == other.uploaded
                and self.uploading == other.uploading
                and self.last_updated == other.last_updated
            )
        return False
