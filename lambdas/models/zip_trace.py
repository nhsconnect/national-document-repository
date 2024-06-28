import uuid
from datetime import datetime, timezone

from enums.metadata_field_names import DocumentZipTraceFields
from enums.zip_trace_status import ZipTraceStatus


class ZipTrace:
    def __init__(self, location: str):
        self.id = uuid.uuid4()
        self.job_id = uuid.uuid4()
        self.created = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.status = ZipTraceStatus(location).PENDING
        self.files_to_download: list[str] = []
        self.location = location

    def to_dict(self):
        zip_trace_metadata = {
            DocumentZipTraceFields.ID.value: str(self.id),
            DocumentZipTraceFields.FILE_LOCATION.value: self.location,
            DocumentZipTraceFields.CREATED.value: self.created,
        }
        return zip_trace_metadata
