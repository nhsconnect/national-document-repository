from enums.snomed_codes import SnomedCode, SnomedCodes
from pydantic import BaseModel


class PdfStitchingSqsMessage(BaseModel):
    nhs_number: str
    snomed_code_doc_type: SnomedCode = SnomedCodes.LLOYD_GEORGE.value
