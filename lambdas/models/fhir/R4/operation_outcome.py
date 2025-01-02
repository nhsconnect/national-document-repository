from typing import List, Literal, Optional

from models.fhir.R4.base_models import CodeableConcept, Coding
from pydantic import BaseModel


class OperationOutcomeCoding(Coding):
    system: Optional[str] = "http://hl7.org/fhir/issue-type"
    code: Optional[str] = None
    display: Optional[str] = None


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
