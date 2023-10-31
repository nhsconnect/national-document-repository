from datetime import datetime
from typing import Literal

from models.config import to_capwords
from pydantic import BaseModel, ConfigDict, Field
from utils.utilities import create_reference_id


class UploadStatusBaseClass(BaseModel):
    model_config = ConfigDict(alias_generator=to_capwords, populate_by_name=True)
    id: str = Field(alias="ID", default_factory=create_reference_id)
    nhs_number: str
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    date: str = Field(default_factory=lambda: date_string_yyyymmdd(datetime.now()))
    file_path: str


class SuccessfulUpload(UploadStatusBaseClass):
    upload_status: Literal["complete"] = "complete"


class FailedUpload(UploadStatusBaseClass):
    upload_status: Literal["failed"] = "failed"
    failure_reason: str


def date_string_yyyymmdd(time_now: datetime) -> str:
    return time_now.strftime("%Y-%m-%d")
