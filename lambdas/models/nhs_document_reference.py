from datetime import datetime, timezone

from enums.metadata_field_names import DocumentReferenceMetadataFields
from pydantic import BaseModel
from utils.utilities import get_file_key_from_s3_url

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class UploadRequestDocument(BaseModel):
    fileName: str
    contentType: str
    docType: str


class NHSDocumentReference:
    def __init__(
        self,
        reference_id: str,
        nhs_number: str,
        file_name: str,
        s3_bucket_name: str,
        content_type: str = "application/pdf",
        current_gp_ods: str = "",
        sub_folder: str = "",
        doc_type: str = "",
        uploading: bool = False,
    ) -> None:
        date_now = datetime.now(timezone.utc)

        self.id = reference_id
        self.nhs_number = nhs_number
        self.content_type = content_type
        self.current_gp_ods = current_gp_ods
        self.file_name = file_name
        self.created = date_now.strftime(DATE_FORMAT)
        self.s3_bucket_name = s3_bucket_name
        self.deleted = ""
        self.virus_scanner_result = "Not Scanned"
        self.uploaded = False
        self.sub_folder = sub_folder
        self.doc_type = doc_type
        self.file_location = self.set_file_location()
        self.uploading = uploading
        self.last_updated = int(date_now.timestamp())

    def set_file_location(self):
        if self.sub_folder != "":
            return f"s3://{self.s3_bucket_name}/{self.sub_folder}/{self.doc_type}/{self.nhs_number}/{self.id}"
        else:
            return f"s3://{self.s3_bucket_name}/{self.nhs_number}/{self.id}"

    def set_deleted(self) -> None:
        self.deleted = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    def set_virus_scanner_result(self, updated_virus_scanner_result) -> None:
        self.virus_scanner_result = updated_virus_scanner_result

    def update_location(self, updated_file_location):
        self.file_location = updated_file_location

    def set_uploaded_to_true(self):
        self.uploaded = True

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
            DocumentReferenceMetadataFields.CURRENT_GP_ODS.value: self.current_gp_ods,
            DocumentReferenceMetadataFields.UPLOADED.value: self.uploaded,
            DocumentReferenceMetadataFields.UPLOADING.value: self.uploading,
            DocumentReferenceMetadataFields.LAST_UPDATED.value: self.last_updated,
        }
        return document_metadata

    @property
    def s3_file_key(self):
        return get_file_key_from_s3_url(self.file_location)

    def __eq__(self, other):
        if isinstance(other, NHSDocumentReference):
            return (
                self.id == other.id
                and self.nhs_number == other.nhs_number
                and self.content_type == other.content_type
                and self.file_name == other.file_name
                and self.created == other.created
                and self.deleted == other.deleted
                and self.virus_scanner_result == other.virus_scanner_result
                and self.file_location == other.file_location
                and self.uploaded == other.uploaded
                and self.uploading == other.uploading
                and self.last_updated == other.last_updated
                and self.sub_folder == other.sub_folder
                and self.doc_type == other.doc_type
            )
        return False
