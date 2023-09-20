import uuid
from datetime import datetime, timezone

from enums.metadata_field_names import DocumentZipTraceFields


class ZipTrace:
    def __init__(self, file_name: str, location: str):
        self.id = uuid.uuid4()
        self.location = location
        self.created = (datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),)
        # self.ttl = ttl
        # self.correlation_id = correlation_id

    def to_dict(self):
        zip_trace_metadata = {
            DocumentZipTraceFields.ID.value: str(self.id),
            DocumentZipTraceFields.FILE_LOCATION.value: self.location,
            DocumentZipTraceFields.CREATED.value: self.created,
        }
        return zip_trace_metadata
