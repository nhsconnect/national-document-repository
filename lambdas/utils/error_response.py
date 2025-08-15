import json

from models.fhir.R4.operation_outcome import (
    OperationOutcome,
    OperationOutcomeCodeableConcept,
    OperationOutcomeCoding,
    OperationOutcomeIssue,
)


class ErrorResponse:
    def __init__(
        self, err_code: str, message: str, interaction_id: str, **kwargs
    ) -> None:
        self.err_code = err_code
        self.message = message
        self.interaction_id = interaction_id
        self.kwargs = kwargs

    def create(self) -> str:
        response = {
            "message": self.message,
            "err_code": self.err_code,
            "interaction_id": self.interaction_id,
            **self.kwargs,
        }
        return json.dumps(response)

    def create_error_fhir_response(self, coding) -> str:
        operation_outcome_coding = OperationOutcomeCoding(
            code=coding.code, display=coding.display, system=coding.system
        )
        operation_outcome_coding_concept = OperationOutcomeCodeableConcept(
            coding=[operation_outcome_coding]
        )
        operation_outcome_issue = OperationOutcomeIssue(
            diagnostics=self.message, details=operation_outcome_coding_concept
        )
        operation_outcome = OperationOutcome(issue=[operation_outcome_issue])
        return operation_outcome.model_dump_json()

    def __eq__(self, other):
        return self.err_code == other.err_code and self.message == other.message
