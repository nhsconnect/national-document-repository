from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

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

    # A temporary field just to allow nhs_number to be known during validation.
    # For the purpose of single source of truth, nhs number should be stored in StagingMetadata, not here
    temp_nhs_number: Optional[str] = Field(
        alias=NHS_NUMBER_FIELD_NAME, exclude=True, default=None
    )

    gp_practice_code: str
    section: str
    sub_section: Optional[str]
    scan_date: str
    scan_id: str
    user_id: str
    upload: str

    @model_validator(mode="after")
    def ensure_gp_practice_code_non_empty(self):
        if not self.gp_practice_code:
            patient_nhs_number = self.temp_nhs_number or "[NHS NUMBER UNKNOWN]"
            raise PydanticCustomError(
                "MissingGPPracticeCode",
                "missing GP-PRACTICE-CODE for patient {patient_nhs_number}",
                {"patient_nhs_number": patient_nhs_number},
            )
        self.temp_nhs_number = None
        return self


class StagingMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nhs_number: str = Field(alias=NHS_NUMBER_FIELD_NAME)
    files: list[MetadataFile]

    retries: int = 0

    @field_validator("nhs_number")
    @classmethod
    def validate_nhs_number(cls, nhs_number: str) -> str:
        if nhs_number.isdigit() and len(nhs_number) == 10:
            return nhs_number

        raise ValueError("NHS number must be a 10 digit number")
