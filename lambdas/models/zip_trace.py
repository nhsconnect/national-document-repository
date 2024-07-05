import uuid
from datetime import datetime, timezone
from typing import Dict

from enums.metadata_field_names import DocumentZipTraceFields
from enums.zip_trace import ZipTraceStatus
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal


class DocumentManifestZipTrace(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal, use_enum_values=True)

    id: str = Field(alias="ID", default_factory=lambda: str(uuid.uuid4()))
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    files_to_download: Dict[str, str]
    job_status: ZipTraceStatus = ZipTraceStatus.PENDING
    zip_file_location: str = ""


class ZipTrace:
    def __init__(self, location: str):
        self.id = uuid.uuid4()
        self.location = location
        self.created = (datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),)

    def to_dict(self):
        zip_trace_metadata = {
            DocumentZipTraceFields.ID.value: str(self.id),
            DocumentZipTraceFields.FILE_LOCATION.value: self.location,
            DocumentZipTraceFields.CREATED.value: self.created,
        }
        return zip_trace_metadata
