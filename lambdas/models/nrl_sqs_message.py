from typing import Optional

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class NrlAttachment(BaseModel):
    content_type: str
    language: str = "en-US"
    url: str
    size: int
    hash: str
    title: str = ""
    creation: str


class NrlSqsMessage(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel)
    )

    nhs_number: str
    snomed_doc_type: str
    snomed_doc_category: str
    description: str = ""
    attachment: Optional[NrlAttachment] = None
    action: str
