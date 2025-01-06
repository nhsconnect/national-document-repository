from enum import Enum

from pydantic import BaseModel


class SnomedCode(BaseModel):
    code: str
    display_name: str


class SnomedCodes(Enum):
    LLOYD_GEORGE = SnomedCode(
        code="16521000000101", display_name="Lloyd George record folder"
    )
    CARE_PLAN = SnomedCode(code="734163000", display_name="Care plan")
    GENERAL_MEDICAL_PRACTICE = SnomedCode(
        code="1060971000000108", display_name="General practice service"
    )
