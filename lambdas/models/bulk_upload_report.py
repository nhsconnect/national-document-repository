from datetime import datetime
from typing import Optional

from enums.metadata_report import MetadataReport
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal
from utils.audit_logging_setup import LoggingService
from utils.utilities import create_reference_id

logger = LoggingService(__name__)


class BulkUploadReport(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal, populate_by_name=True)
    id: str = Field(alias=MetadataReport.ID, default_factory=create_reference_id)
    nhs_number: str = Field(alias=MetadataReport.NhsNumber)
    upload_status: str = Field(alias=MetadataReport.UploadStatus)
    timestamp: int = Field(
        alias=MetadataReport.Timestamp,
        default_factory=lambda: int(datetime.now().timestamp()),
    )
    date: str = Field(
        alias=MetadataReport.Date,
        default_factory=lambda: date_string_yyyymmdd(datetime.now()),
    )
    file_path: str = Field(alias=MetadataReport.FilePath)
    pds_ods_code: str = Field(default="", alias=MetadataReport.PdsOdsCode)
    uploader_ods_code: str = Field(default="", alias=MetadataReport.UploaderOdsCode)
    failure_reason: Optional[str] = Field(
        default="", alias=MetadataReport.FailureReason
    )


def date_string_yyyymmdd(time_now: datetime) -> str:
    return time_now.strftime("%Y-%m-%d")
