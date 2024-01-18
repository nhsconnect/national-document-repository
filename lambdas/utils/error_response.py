import json
from enum import Enum


class ErrorResponse:
    def __init__(self, err_code: str, message: str) -> None:
        self.err_code = err_code
        self.message = message

    def create(self) -> str:
        return json.dumps({"message": self.message, "err_code": self.err_code})

    def __eq__(self, other):
        return self.error_code == other.error_code and self.message == other.message


class LambdaError(Enum):
    """
    Errors for SearchPatientException
    """

    SearchPatientMissing = {"err_code": "SP_1001", "message": "Missing user details"}
    SearchPatientNoPDS = {
        "err_code": "SP_1002",
        "message": "Patient does not exist for given NHS number",
    }
    SearchPatientNoAuth = {
        "err_code": "SP_1003",
        "message": "Patient does not exist for given NHS number",
    }
    SearchPatientNoId = {
        "err_code": "SP_1004",
        "message": "An error occurred while searching for patient",
    }
    SearchPatientNoParse = {
        "err_code": "SP_1005",
        "message": "Failed to parse PDS data",
    }

    """
       Errors for CreateDocumentRefException
    """
    CreateDocNoBody = {"err_code": "CDR_1001", "message": "Missing event body"}
    CreateDocPayload = {"err_code": "CDR_1002", "message": "Invalid json in body"}
    CreateDocProps = {
        "err_code": "CDR_1003",
        "message": "Request body missing some properties",
    }
    CreateDocFiles = {"err_code": "CDR_1004", "message": "Invalid files or id"}
    CreateDocNoParse = {
        "err_code": "CDR_1005",
        "message": "Failed to parse document upload request data",
    }
    CreateDocNoType = {
        "err_code": "CDR_1006",
        "message": "Failed to parse document upload request data",
    }
    CreateDocInvalidType = {
        "err_code": "CDR_1007",
        "message": "Failed to parse document upload request data",
    }
    CreateDocPresign = {"err_code": "CDR_5001", "message": "Internal error"}
    CreateDocUpload = {"err_code": "CDR_5002", "message": "Internal error"}

    """
       Errors for InvalidDocTypeException
    """
    DocTypeDB = {
        "err_code": "DT_5001",
        "message": "Failed to resolve dynamodb table name for this document",
    }

    """
       Errors for LoginRedirectException
    """
    RedirectInternal = {
        "err_code": "LR_5001",
        "message": "Server error",
    }

    """
       Errors for LoginException
    """
    LoginNoState = {
        "err_code": "LIN_1001",
        "message": "No auth err_code and/or state in the query string parameters",
    }
    LoginBadState = {
        "err_code": "LIN_2001",
        "message": "Unrecognised state value",
    }

    LoginBadAuth = {
        "err_code": "LIN_2002",
        "message": "Cannot log user in, expected information from CIS2 is missing",
    }
    LoginNoOrg = {
        "err_code": "LIN_2003",
        "message": "No org found for given ODS err_code",
    }
    LoginNullOrgs = {"err_code": "LIN_2004", "message": "No orgs found for user"}
    LoginNoRole = {
        "err_code": "LIN_2005",
        "message": "Unable to remove used state value",
    }
    LoginValidate = {
        "err_code": "LIN_5001",
        "message": "Unrecognised state value",
    }
    LoginNoContact = {
        "err_code": "LIN_5002",
        "message": "Issue when contacting CIS2",
    }
    LoginOds = {"err_code": "LIN_5003", "message": "Bad response from ODS API"}
    LoginStateFault = {
        "err_code": "LIN_5004",
        "message": "Unable to remove used state value",
    }
    LoginBadSSM = {
        "err_code": "LIN_5005",
        "message": "Failed to find SSM parameter value for user role",
    }
    LoginNoSSM = {
        "err_code": "LIN_5006",
        "message": "Failed to find SSM parameter value for user role",
    }
    LoginSmartSSM = {
        "err_code": "LIN_5007",
        "message": "Failed to find SSM parameter value for smartcard",
    }
    LoginPcseSSM = {
        "err_code": "LIN_5008",
        "message": "Failed to find SSM parameter value for PCSE role",
    }
    LoginGpSSM = {
        "err_code": "LIN_5009",
        "message": "Failed to find SSM parameter value for GP role",
    }
    LoginPcseODS = {
        "err_code": "LIN_5010",
        "message": "SSM parameter values for PSCE ODS err_code may not exist",
    }

    """
       Errors for DocumentManifestServiceException
    """
    ManifestNoDocs = {
        "err_code": "DMS_4001",
        "message": "No documents found for given NHS number and document type",
    }
    ManifestValidation = {
        "err_code": "DMS_5001",
        "message": "Failed to parse document reference from from DynamoDb response",
    }
    ManifestDB = {
        "err_code": "DMS_5002",
        "message": "Failed to create document manifest",
    }
    ManifestClient = {
        "err_code": "DMS_5003",
        "message": "Failed to create document manifest",
    }

    """
       Errors for LGStitchServiceException
    """
    StitchNotFound = {
        "err_code": "LGS_4001",
        "message": "Lloyd george record not found for patient",
    }
    StitchNoService = {
        "err_code": "LGS_5001",
        "message": "Unable to retrieve documents for patient",
    }
    StitchNoClient = {
        "err_code": "LGS_5002",
        "message": "Unable to return stitched pdf file due to internal error",
    }
    StitchClient = {
        "err_code": "LGS_5003",
        "message": "Unable to retrieve documents for patient",
    }
    StitchFailed = {
        "err_code": "LGS_5004",
        "message": "Unable to retrieve documents for patient",
    }

    """
       Errors for DocumentRefSearchException
    """
    DocRefClient = {
        "err_code": "DRS_5001",
        "message": "An error occurred when searching for available documents",
    }

    """
       Errors for DocumentDeletionServiceException
    """
    DocDelClient = {
        "err_code": "DDS_5001",
        "message": "Failed to delete documents",
    }

    """
       Errors with no exception
    """
    DocDelNull = {
        "err_code": "DDS_4001",
        "message": "Failed to delete documents",
    }
    LoginNoAuth = {
        "err_code": "LIN_1002",
        "message": "No auth err_code and/or state in the query string parameters",
    }
    LogoutClient = {
        "err_code": "OUT_5001",
        "message": "Error logging user out",
    }
    LogoutAuth = {"err_code": "OUT_4001", "message": "Invalid Authorization header"}
    EnvMissing = {
        "err_code": "ENV_5001",
        "message": "An error occurred due to missing environment variable: '%name%'",
    }
    DocTypeNull = {"err_code": "VDT_4001", "message": "docType not supplied"}
    DocTypeInvalid = {
        "err_code": "VDT_4002",
        "message": "Invalid document type requested",
    }
    DocTypeKey = {
        "err_code": "VDT_4003",
        "message": "An error occurred due to missing key",
    }
    PatientIdInvalid = {
        "err_code": "PN_4001",
        "message": "Invalid patient number %number%",
    }
    PatientIdNoKey = {
        "err_code": "PN_4002",
        "message": "An error occurred due to missing key",
    }
    GatewayError = {
        "err_code": "GWY_5001",
        "message": "Failed to utilise AWS client/resource",
    }
