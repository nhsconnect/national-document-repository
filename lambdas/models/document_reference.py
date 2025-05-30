import pathlib
from datetime import datetime, timezone
from typing import Optional

from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.supported_document_types import SupportedDocumentTypes
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel, to_pascal

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class UploadRequestDocument(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    fileName: str
    contentType: str
    docType: SupportedDocumentTypes
    clientId: str


class UploadDocumentReference(BaseModel):
    reference: str = Field(...)
    doc_type: SupportedDocumentTypes = Field(..., alias="type")
    fields: dict[str, bool] = Field(...)


class UploadDocumentReferences(BaseModel):
    files: list[UploadDocumentReference] = Field(...)


class SearchDocumentReference(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
    id: str
    created: str
    file_name: str
    virus_scanner_result: str
    file_size: int


class DocumentReference(BaseModel):
    model_config = ConfigDict(
        validate_by_alias=True,
        validate_by_name=True,
        alias_generator=to_pascal,
        use_enum_values=True,
        populate_by_name=True,
    )

    id: str = Field(..., alias=str(DocumentReferenceMetadataFields.ID.value))
    content_type: str = Field(default="application/pdf")
    created: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime(DATE_FORMAT)
    )
    current_gp_ods: str = Field(default="")
    deleted: str = Field(default="")
    file_name: str
    nhs_number: str
    ttl: Optional[int] = Field(
        alias=str(DocumentReferenceMetadataFields.TTL.value), default=None
    )
    virus_scanner_result: str = Field(default="Not Scanned")
    uploaded: bool = Field(default=False)
    uploading: bool = Field(default=False)
    last_updated: int = Field(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp()),
    )
    s3_bucket_name: str = Field(exclude=True, default=None)
    s3_file_key: str = Field(exclude=True, default=None)
    sub_folder: str = Field(default=None, exclude=True)
    doc_type: str = Field(default=None, exclude=True)
    file_location: str = ""

    @model_validator(mode="before")
    @classmethod
    def set_location_properties(cls, data, *args, **kwargs):
        if "file_location" in data or "FileLocation" in data:
            file_location = data.get("file_location") or data.get("FileLocation")
            data["s3_bucket_name"], data["s3_file_key"] = file_location.replace(
                "s3://", ""
            ).split("/", 1)
        elif "s3_bucket_name" in data:
            data["file_location"] = f"s3://{data['s3_bucket_name']}"
            s3_file_key = ""
            if "sub_folder" in data:
                s3_file_key += f"/{data['sub_folder']}"
                if "doc_type" in data:
                    s3_file_key += f"/{data['sub_folder']}"
            s3_file_key += f"/{data['nhs_number']}/{data['id']}"
            data["file_location"] += s3_file_key
            data["s3_file_key"] = (
                s3_file_key[1:] if s3_file_key.startswith("/") else s3_file_key
            )

        return data

    def get_file_name_path(self):
        return pathlib.Path(self.file_name)

    def get_base_name(self):
        return self.get_file_name_path().stem

    def get_file_extension(self):
        return self.get_file_name_path().suffix

    def create_unique_filename(self, duplicates: int):
        return f"{self.get_base_name()}({duplicates}){self.get_file_extension()}"

    def last_updated_within_three_minutes(self) -> bool:
        three_minutes_ago = datetime.now(timezone.utc).timestamp() - 60 * 3
        return self.last_updated >= three_minutes_ago

    def set_deleted(self) -> None:
        self.deleted = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    def set_virus_scanner_result(self, updated_virus_scanner_result) -> None:
        self.virus_scanner_result = updated_virus_scanner_result

    def set_uploaded_to_true(self):
        self.uploaded = True
