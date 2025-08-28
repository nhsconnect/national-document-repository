from typing import List, Literal, Optional

from enums.fhir.fhir_issue_type import FhirIssueCoding
from models.fhir.R4.base_models import CodeableConcept, Coding
from pydantic import BaseModel


class OperationOutcomeCoding(Coding):
    system: Optional[str] = FhirIssueCoding.EXCEPTION.system
    code: Optional[str] = FhirIssueCoding.EXCEPTION.code
    display: Optional[str] = FhirIssueCoding.EXCEPTION.display


class OperationOutcomeCodeableConcept(CodeableConcept):
    coding: List[OperationOutcomeCoding]


class OperationOutcomeIssue(BaseModel):
    severity: str = "error"
    code: str = "exception"
    details: Optional[OperationOutcomeCodeableConcept] = None
    diagnostics: Optional[str] = None


class OperationOutcome(BaseModel):
    resourceType: Literal["OperationOutcome"] = "OperationOutcome"
    issue: List[OperationOutcomeIssue]
