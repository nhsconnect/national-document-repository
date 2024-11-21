from typing import Optional

from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class MNSMessageSubject(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    nhs_number: str
    family_name: str
    dob: str


class MNSSQSMessage(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    id: str
    type: str
    subject: MNSMessageSubject
    source: Optional[dict] = None
    time: Optional[str] = None
    data: Optional[dict] = None
