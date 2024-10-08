import uuid
from datetime import datetime, timezone

from enums.trace_status import TraceStatus
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel, to_pascal


class StitchTrace(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_pascal,
        use_enum_values=True,
        populate_by_name=True,
    )

    id: str = Field(alias="ID", default_factory=lambda: str(uuid.uuid4()))
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    job_status: TraceStatus = TraceStatus.PENDING
    stitched_file_location: str = ""
    nhs_number: str
    number_of_files: int = 0
    file_last_updated: str = ""
    total_file_size_in_byte: int = 0
    ttl: int = Field(alias="TTL", default=None)


class DocumentStitchJob(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, use_enum_values=True)

    job_status: TraceStatus
    presigned_url: str
    number_of_files: int = 0
    last_updated: str = ""
    total_file_size_in_byte: int = 0
