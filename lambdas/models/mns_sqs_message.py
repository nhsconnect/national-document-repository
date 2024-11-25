from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class MNSMessageSubject(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel),
    )
    nhs_number: str


class MNSSQSMessage(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(validation_alias=to_camel),
    )
    id: str
    type: str
    subject: MNSMessageSubject
    data: dict
