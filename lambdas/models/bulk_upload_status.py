from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter


class SuccessfulUpload(BaseModel):
    id: str = Field(alias="ID")
    nhs_number: str
    timestamp: str
    upload_status: Literal["complete"]
    file_location_in_bucket: str


class FailedUpload(BaseModel):
    id: str = Field(alias="ID")
    nhs_number: str
    timestamp: str
    upload_status: Literal["failed"]
    failure_reason: str
    file_path_of_failed_file: str


UploadStatus = TypeAdapter(
    Annotated[
        Union[SuccessfulUpload, FailedUpload], Field(..., discriminator="upload_status")
    ]
)
