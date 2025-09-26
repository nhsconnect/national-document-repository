from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError

METADATA_FILENAME = "metadata.csv"
NHS_NUMBER_FIELD_NAME = "NHS-NO"
ODS_CODE = "GP-PRACTICE-CODE"
NHS_NUMBER_PLACEHOLDER = "0000000000"


def to_upper_case_with_hyphen(field_name: str) -> str:
    return field_name.upper().replace("_", "-")


class MetadataFile(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_upper_case_with_hyphen, validate_by_name=True
    )

    file_path: str = Field(alias="FILEPATH")
    stored_file_name: Optional[str] = Field(alias="STORED-FILE-NAME", default=None)
    page_count: str = Field(alias="PAGE COUNT")
    nhs_number: Optional[str] = Field(
        alias=NHS_NUMBER_FIELD_NAME, exclude=True, default=None
    )
    gp_practice_code: str
    section: str
    sub_section: Optional[str]
    scan_date: str
    scan_id: str
    user_id: str
    upload: str

    @field_validator("stored_file_name", mode="after")
    def default_stored_file_name(cls, value, info):
        if value is None:
            return info.data.get("file_path")
        return value

    # @model_validator(mode="before")
    # @classmethod
    # def default_stored_file_name(cls, data):
    #     if "STORED-FILE-NAME" not in data or data["STORED-FILE-NAME"] is None:
    #         data["STORED-FILE-NAME"] = data.get("FILEPATH")
    #     return data

    @field_validator("gp_practice_code")
    @classmethod
    def ensure_gp_practice_code_non_empty(
        cls, gp_practice_code: str, info: ValidationInfo
    ) -> str:
        if not gp_practice_code:
            patient_nhs_number = info.data.get("nhs_number", "")
            raise PydanticCustomError(
                "MissingGPPracticeCode",
                "missing GP-PRACTICE-CODE for patient {patient_nhs_number}",
                {"patient_nhs_number": patient_nhs_number},
            )
        return gp_practice_code

    # def model_post_init(self, __context):
    #     # Ensures stored_file_name is set after model initialization or copying
    #     if self.stored_file_name is None:
    #         self.stored_file_name = self.file_path

class StagingMetadata(BaseModel):
    model_config = ConfigDict(validate_by_name=True)

    nhs_number: str = Field(default=NHS_NUMBER_PLACEHOLDER, alias=NHS_NUMBER_FIELD_NAME)
    files: list[MetadataFile]
    retries: int = 0

    @field_validator("nhs_number")
    @classmethod
    def validate_nhs_number(cls, nhs_number: str) -> str:
        if nhs_number and nhs_number.isdigit():
            return nhs_number

        return NHS_NUMBER_PLACEHOLDER
