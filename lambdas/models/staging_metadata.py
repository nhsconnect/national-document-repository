from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

METADATA_FILENAME = "metadata.csv"
NHS_NUMBER_FIELD_NAME = "NHS-NO"


def to_upper_case_with_hyphen(field_name: str) -> str:
    return field_name.upper().replace("_", "-")


class MetadataFile(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_upper_case_with_hyphen, populate_by_name=True
    )

    file_path: str = Field(alias="FILEPATH")
    page_count: str = Field(alias="PAGE COUNT")
    gp_practice_code: str
    section: str
    sub_section: Optional[str]
    scan_date: str
    scan_id: str
    user_id: str
    upload: str


class StagingMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nhs_number: str = Field(alias=NHS_NUMBER_FIELD_NAME)
    files: list[MetadataFile]
