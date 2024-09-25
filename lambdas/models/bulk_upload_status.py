from datetime import datetime
from typing import Optional

from enums.upload_status import UploadStatus
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal
from utils.utilities import create_reference_id


class BulkUploadReport(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True)
    id: str = Field(alias="ID", default_factory=create_reference_id)
    nhs_number: str
    upload_status: UploadStatus
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    date: str = Field(default_factory=lambda: date_string_yyyymmdd(datetime.now()))
    file_path: str
    pds_ods_code: str = ""
    uploader_ods_code: str = ""
    failure_reason: Optional[str] = None


def date_string_yyyymmdd(time_now: datetime) -> str:
    return time_now.strftime("%Y-%m-%d")


class OdsReport:
    def __init__(
        self,
        uploader_ods_code: str,
        total_successful: int = 0,
        total_registered_elsewhere: int = 0,
        total_suspended: int = 0,
        failure_reasons: dict = {},
    ):
        self.uploader_ods_code = uploader_ods_code
        self.total_successful = total_successful
        self.total_registered_elsewhere = total_registered_elsewhere
        self.total_suspended = total_suspended
        self.failure_reasons = failure_reasons
