from typing import Optional

from pydantic import BaseModel, Field

METADATA_FILENAME = "metadata.csv"


class MetadataFile(BaseModel):
    file_path: str
    page_count: str
    gp_practice_code: str
    nhs_number: str = Field(exclude=True)
    section: str
    sub_section: Optional[str]
    scan_date: str
    scan_id: str
    user_id: str
    upload: str


class StagingMetadata(BaseModel):
    nhs_number: str
    files: list[MetadataFile]
