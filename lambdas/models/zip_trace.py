from datetime import datetime, timezone
from typing import Dict

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


def format_day_time_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ZipTrace(BaseModel):
    conf = ConfigDict(alias_generator=to_camel)

    id: str
    job_id: str
    created: str = Field(default_factory=format_day_time_now)
    files_to_download: Dict[str, str]
    status: str
    zip_file_location: str = ""
