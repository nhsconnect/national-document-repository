from enums.snomed_codes import SnomedCode
from pydantic import BaseModel


class PdfStitchingSqsMessage(BaseModel):
    nhs_number: str
    snomed_code_doc_type: SnomedCode
