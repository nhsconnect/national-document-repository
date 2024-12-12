import json

from fhir.resources.R4B.operationoutcome import OperationOutcome


class ErrorResponse:
    def __init__(self, err_code: str, message: str, interaction_id: str) -> None:
        self.err_code = err_code
        self.message = message
        self.interaction_id = interaction_id

    def create(self) -> str:
        return json.dumps(
            {
                "message": self.message,
                "err_code": self.err_code,
                "interaction_id": self.interaction_id,
            }
        )

    def create_error_fhir_response(self) -> str:
        operation_outcome = OperationOutcome.construct()
        operation_outcome.severity = "error"
        operation_outcome.code = self.err_code
        operation_outcome.details = self.message
        return operation_outcome.json()

    def __eq__(self, other):
        return self.err_code == other.err_code and self.message == other.message
