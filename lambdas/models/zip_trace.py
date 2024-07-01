import uuid
from datetime import date, datetime, timezone
from typing import Dict

from enums.metadata_field_names import DocumentZipTraceFields
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


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


class ZipTraceModel(BaseModel):
    conf = ConfigDict(alias_generator=to_camel)

    id: str
    job_id: str
    created: date
    files_to_download: Dict[str, str]
    status: str
    zip_file_location: str
