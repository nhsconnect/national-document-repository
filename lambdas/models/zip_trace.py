import uuid
from datetime import datetime, timezone
from typing import Dict

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_pascal


class DocumentManifestZipTrace(BaseModel):
    model_config = ConfigDict(alias_generator=to_pascal)

    id: str = Field(alias="ID", default_factory=lambda: str(uuid.uuid4()))
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created: str = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )
    files_to_download: Dict[str, str]
    status: str = ""
    zip_file_location: str = ""
