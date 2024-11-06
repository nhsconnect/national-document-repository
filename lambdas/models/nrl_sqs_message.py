from typing import Optional

from enums.snomed_codes import SnomedCodesCatagory, SnomedCodesType
from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class NrlAttachment(BaseModel):
    content_type: str = ""
    language: str = "en-US"
    url: str = ""
    size: int = 0
    hash: str = ""
    title: str = ""
    creation: str = ""


class NrlSqsMessage(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel)
    )

    nhs_number: str
    snomed_code_doc_type: str = SnomedCodesType.LLOYD_GEORGE
    snomed_code_category: str = SnomedCodesCatagory.CARE_PLAN
    description: str = ""
    attachment: Optional[NrlAttachment] = None
    action: str
