from typing import List, Literal, Optional

from pydantic import BaseModel


class Coding(BaseModel):
    system: Optional[str] = "http://hl7.org/fhir/issue-type"
    code: Optional[str] = None
    display: Optional[str] = None


class CodeableConcept(BaseModel):
    coding: Optional[List[Coding]] = None


class OperationOutcomeIssue(BaseModel):
    severity: str = "error"
    code: str = "exception"
    details: Optional[CodeableConcept] = None
    diagnostics: Optional[str] = None


class OperationOutcome(BaseModel):
    resourceType: Literal["OperationOutcome"] = "OperationOutcome"
    issue: List[OperationOutcomeIssue]
