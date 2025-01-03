from typing import Optional

from enums.snomed_codes import SnomedCode, SnomedCodes
from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class NrlAttachment(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        use_enum_values=True,
    )
    content_type: str = "application/pdf"
    language: str = "en-UK"
    url: str = None


class NrlSqsMessage(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        use_enum_values=True,
    )

    nhs_number: str
    snomed_code_doc_type: SnomedCode = SnomedCodes.LLOYD_GEORGE.value
    snomed_code_category: SnomedCode = SnomedCodes.CARE_PLAN.value
    snomed_code_practice_setting: SnomedCode = (
        SnomedCodes.GENERAL_MEDICAL_PRACTICE.value
    )
    description: str = ""
    attachment: Optional[NrlAttachment] = None
    action: str
