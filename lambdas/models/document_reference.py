import pathlib

from enums.metadata_field_names import DocumentReferenceMetadataFields
from pydantic import BaseModel, Field
from utils.exceptions import InvalidDocumentReferenceException


class DocumentReferenceSearchResult(BaseModel):
    created: str = Field(..., alias="created")
    fileName: str = Field(..., alias="file_name")
    virusScannerResult: str = Field(..., alias="virus_scanner_result")


class DocumentReference(BaseModel):
    id: str = Field(..., alias=str(DocumentReferenceMetadataFields.ID.value))
    content_type: str = Field(
        ..., alias=str(DocumentReferenceMetadataFields.CONTENT_TYPE.value)
    )
    created: str = Field(..., alias=str(DocumentReferenceMetadataFields.CREATED.value))
    deleted: str = Field(..., alias=str(DocumentReferenceMetadataFields.DELETED.value))
    file_location: str = Field(
        ..., alias=str(DocumentReferenceMetadataFields.FILE_LOCATION.value)
    )
    file_name: str = Field(
        ..., alias=str(DocumentReferenceMetadataFields.FILE_NAME.value)
    )
    nhs_number: str = Field(
        ..., alias=str(DocumentReferenceMetadataFields.NHS_NUMBER.value)
    )
    virus_scanner_result: str = Field(
        ..., alias=str(DocumentReferenceMetadataFields.VIRUS_SCANNER_RESULT.value)
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

    def create_unique_filename(self, duplicates):
        return f"{self.get_base_name()}({duplicates}){self.get_file_extension()}"

    def __eq__(self, other):
        if isinstance(self, DocumentReference):
            return (
                self.id == other.id
                and self.ContentType == other.ContentType
                and self.Created == other.Created
                and self.Deleted == other.Deleted
                and self.FileLocation == other.FileLocation
                and self.FileName == other.FileName
                and self.NhsNumber == other.NhsNumber
                and self.VirusScannerResult == other.VirusScannerResult
            )
        return False
