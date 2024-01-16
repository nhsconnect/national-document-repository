import json
from enum import Enum

class ErrorResponse:
    def __init__(
        self, error_code: str, message: str
    ) -> None:
        self.error_code = error_code
        self.message = message

    def create(self) -> str:
        return json.dump({"message": self.message, "err_code": self.error_code})

    def __eq__(self, other):
        return (
            self.error_code == other.error_code
            and self.message == other.message
        )

class LambdaError(Enum):
    SearchPatientMissing = {"code": "SP_1001", "message": "Missing user details"},
    SearchPatientNoPDS = {"code": "SP_1002", "message": "Patient does not exist for given NHS number"}
    SearchPatientNoAuth = {"code": "SP_1003", "message": "Patient does not exist for given NHS number"}
    SearchPatientNoId = {"code": "SP_1004", "message": "An error occurred while searching for patient"}
    SearchPatientNoParse = {"code": "SP_1005", "message": "Failed to parse PDS data"}