from typing import Optional

from enums.snomed_codes import SnomedCode, SnomedCodes
from models.fhir.R4.nrl_fhir_document_reference import Attachment
from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


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
    attachment: Optional[Attachment] = None
    action: str
