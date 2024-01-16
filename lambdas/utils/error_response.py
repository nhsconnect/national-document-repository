import json
from enum import Enum


class ErrorResponse:
    def __init__(self, error_code: str, message: str) -> None:
        self.error_code = error_code
        self.message = message

    def create(self) -> str:
        return json.dump({"message": self.message, "err_code": self.error_code})

    def __eq__(self, other):
        return self.error_code == other.error_code and self.message == other.message


class LambdaError(Enum):
    SearchPatientMissing = ({"code": "SP_1001", "message": "Missing user details"},)
    SearchPatientNoPDS = {
        "code": "SP_1002",
        "message": "Patient does not exist for given NHS number",
    }
    SearchPatientNoAuth = {
        "code": "SP_1003",
        "message": "Patient does not exist for given NHS number",
    }
    SearchPatientNoId = {
        "code": "SP_1004",
        "message": "An error occurred while searching for patient",
    }
    SearchPatientNoParse = {"code": "SP_1005", "message": "Failed to parse PDS data"}

    CreateDocNoBody = {"code": "CDR_1001", "message": "Missing event body"}
    CreateDocPayload = {"code": "CDR_1002", "message": "Invalid json in body"}
    CreateDocProps = {
        "code": "CDR_1003",
        "message": "Request body missing some properties",
    }
    CreateDocFiles = {"code": "CDR_1004", "message": "Invalid files or id"}
    CreateDocNoParse = {
        "code": "CDR_1005",
        "message": "Failed to parse document upload request data",
    }
    CreateDocNoType = {
        "code": "CDR_1006",
        "message": "Failed to parse document upload request data",
    }
    CreateDocInvalidType = {
        "code": "CDR_1007",
        "message": "Failed to parse document upload request data",
    }
    CreateDocPresign = {"code": "CDR_5001", "message": "Internal error"}
    CreateDocUpload = {"code": "CDR_5002", "message": "Internal error"}

    DocTypeInvalid = {
        "code": "DT_5001",
        "message": "Failed to resolve dynamodb table name for this document",
    }
