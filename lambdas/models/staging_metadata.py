import csv
import json
from typing import Optional
from pydantic import BaseModel


class MetadataFile(BaseModel):
    file_path: str
    page_count: str
    gp_practice_code: str
    section: str
    sub_section: Optional[str]
    scan_date: str
    scan_id: str
    user_id: str
    upload: str


class StagingMetadata(BaseModel):
    nhs_number: int
    files: list[MetadataFile]

