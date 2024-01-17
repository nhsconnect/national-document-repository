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
    """
    Errors for SearchPatientException
    """

    SearchPatientMissing = {"code": "SP_1001", "message": "Missing user details"}
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

    """
       Errors for CreateDocumentRefException
    """
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

    """
       Errors for InvalidDocTypeException
    """
    DocTypeInvalid = {
        "code": "DT_5001",
        "message": "Failed to resolve dynamodb table name for this document",
    }

    """
       Errors for LoginException
    """
    LoginNoState = {
        "code": "LIN_1001",
        "message": "No auth code and/or state in the query string parameters",
    }
    LoginNoKey = {
        "code": "LIN_1002",
        "message": "No auth code and/or state in the query string parameters",
    }
    LoginBadState = {
        "code": "LIN_2001",
        "message": "Unrecognised state value",
    }
    LoginValidate = {
        "code": "LIN_5001",
        "message": "Unrecognised state value",
    }
    LoginNoContact = {
        "code": "LIN_5002",
        "message": "Issue when contacting CIS2",
    }
    LoginBadAuth = {
        "code": "LIN_2002",
        "message": "Cannot log user in, expected information from CIS2 is missing",
    }
    LoginOds = {"code": "LIN_5003", "message": "Bad response from ODS API"}
    LoginNoOrg = {"code": "LIN_2003", "message": "No org found for given ODS code"}
    LoginNullOrgs = {"code": "LIN_2004", "message": "No orgs found for user"}
    LoginStateFault = {
        "code": "LIN_5004",
        "message": "Unable to remove used state value",
    }
    LoginNoRole = {"code": "LIN_2005", "message": "Unable to remove used state value"}
