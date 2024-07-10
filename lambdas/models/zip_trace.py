import uuid
from datetime import datetime, timezone
from typing import Dict

from enums.zip_trace import ZipTraceStatus
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel, to_pascal


class DocumentManifestZipTrace(BaseModel):
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
    files_to_download: Dict[str, str]
    job_status: ZipTraceStatus = ZipTraceStatus.PENDING
    zip_file_location: str = ""

    @staticmethod
    def get_field_names_alias_list() -> list[str | None]:
        return [field.alias for field in DocumentManifestZipTrace.model_fields.values()]


class DocumentManifestJob(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, use_enum_values=True)

    job_status: ZipTraceStatus
    url: str
