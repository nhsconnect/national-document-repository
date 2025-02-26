from enums.snomed_codes import SnomedCode, SnomedCodes
from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PdfStitcherSqsMessage(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
    )

    nhs_number: str
    snomed_code_doc_type: SnomedCode = SnomedCodes.LLOYD_GEORGE.value
