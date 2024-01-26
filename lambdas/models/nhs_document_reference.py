from datetime import datetime, timezone

from enums.metadata_field_names import DocumentReferenceMetadataFields
from pydantic import BaseModel


class UploadRequestDocument(BaseModel):
    fileName: str
    contentType: str
    docType: str


class NHSDocumentReference:
    def __init__(
        self,
        reference_id: str,
        nhs_number,
        file_name: str,
        s3_bucket_name: str,
        content_type: str = "application/pdf",
        current_gp_ods: str = "",
    ) -> None:
        self.id = reference_id
        self.nhs_number = nhs_number
        self.content_type = content_type
        self.current_ods_code = current_gp_ods
        self.file_name = file_name
        self.created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.s3_bucket_name = s3_bucket_name
        self.deleted = ""
        self.virus_scanner_result = "Not Scanned"
        self.file_location = f"s3://{self.s3_bucket_name}/{self.s3_file_key}"

    def set_deleted(self) -> None:
        self.deleted = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def set_virus_scanner_result(self, updated_virus_scanner_result) -> None:
        self.virus_scanner_result = updated_virus_scanner_result

    def update_location(self, updated_file_location):
        self.file_location = updated_file_location

    def to_dict(self):
        document_metadata = {
            DocumentReferenceMetadataFields.ID.value: str(self.id),
            DocumentReferenceMetadataFields.NHS_NUMBER.value: self.nhs_number,
            DocumentReferenceMetadataFields.FILE_NAME.value: self.file_name,
            DocumentReferenceMetadataFields.FILE_LOCATION.value: self.file_location,
            DocumentReferenceMetadataFields.CREATED.value: self.created,
            DocumentReferenceMetadataFields.DELETED.value: self.deleted,
            DocumentReferenceMetadataFields.CONTENT_TYPE.value: self.content_type,
            DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT.value: self.virus_scanner_result,
            DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: self.current_ods_code,
        }
        return document_metadata

    @property
    def s3_file_key(self):
        return f"{self.nhs_number}/{self.id}"

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.nhs_number == other.nhs_number
            and self.content_type == other.content_type
            and self.file_name == other.file_name
            and self.created == other.created
            and self.deleted == other.deleted
            and self.virus_scanner_result == other.virus_scanner_result
            and self.file_location == other.file_location
        )
