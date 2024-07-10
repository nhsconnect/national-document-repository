from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal
from utils.utilities import create_reference_id


class UploadStatusBaseClass(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True)
    id: str = Field(alias="ID", default_factory=create_reference_id)
    nhs_number: str

    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    date: str = Field(default_factory=lambda: date_string_yyyymmdd(datetime.now()))
    file_path: str
    pds_ods_code: str = ""
    uploader_ods_code: str = ""


class SuccessfulUpload(UploadStatusBaseClass):
    upload_status: Literal["complete"] = "complete"


class FailedUpload(UploadStatusBaseClass):
    upload_status: Literal["failed"] = "failed"
    failure_reason: str


FieldNamesForBulkUploadReport = [
    "NhsNumber",
    "UploadStatus",
    "FailureReason",
    "PdsOdsCode",
    "UploaderOdsCode",
    "FilePath",
    "Date",
    "Timestamp",
    "ID",
]


def date_string_yyyymmdd(time_now: datetime) -> str:
    return time_now.strftime("%Y-%m-%d")
