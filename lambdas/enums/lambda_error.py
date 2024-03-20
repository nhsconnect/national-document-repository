from enum import Enum
from typing import Optional

from utils.error_response import ErrorResponse
from utils.request_context import request_context


class LambdaError(Enum):
    def create_error_body(self, params: Optional[dict] = None) -> str:
        err_code = self.value["err_code"]
        message = self.value["message"]
        if "%" in message and params:
            message = message % params

        interaction_id = getattr(request_context, "request_id", None)
        error_response = ErrorResponse(
            err_code=err_code, message=message, interaction_id=interaction_id
        )
        return error_response.create()

    def to_str(self) -> str:
        return f"[{self.value['err_code']}] {self.value['message']}"

    """
    Errors for SearchPatientException
    """

    SearchPatientMissing = {"err_code": "SP_4001", "message": "Missing user details"}
    SearchPatientNoPDS = {
        "err_code": "SP_4002",
        "message": "Patient does not exist for given NHS number",
    }
    SearchPatientNoAuth = {
        "err_code": "SP_4003",
        "message": "Patient does not exist for given NHS number",
    }
    SearchPatientNoId = {
        "err_code": "SP_4004",
        "message": "An error occurred while searching for patient",
    }
    SearchPatientNoParse = {
        "err_code": "SP_4005",
        "message": "Failed to parse PDS data",
    }

    """
       Errors for CreateDocumentRefException
    """
    CreateDocNoBody = {"err_code": "CDR_4001", "message": "Missing event body"}
    CreateDocPayload = {"err_code": "CDR_4002", "message": "Invalid json in body"}
    CreateDocProps = {
        "err_code": "CDR_4003",
        "message": "Request body missing some properties",
    }
    CreateDocFiles = {"err_code": "CDR_4004", "message": "Invalid files or id"}
    CreateDocNoParse = {
        "err_code": "CDR_4005",
        "message": "Failed to parse document upload request data",
    }
    CreateDocNoType = {
        "err_code": "CDR_4006",
        "message": "Failed to parse document upload request data",
    }
    CreateDocInvalidType = {
        "err_code": "CDR_4007",
        "message": "Failed to parse document upload request data",
    }
    CreateDocRecordAlreadyInPlace = {
        "err_code": "CDR_4008",
        "message": "The patient already has a full set of record.",
    }
    CreateDocStillUploading = {
        "err_code": "CDR_4230",
        "message": "The patients record is in the process of being uploaded, please try again in three minutes",
    }
    CreateDocPresign = {
        "err_code": "CDR_5001",
        "message": "An error occurred when creating pre-signed url for document reference",
    }
    CreateDocUpload = {
        "err_code": "CDR_5002",
        "message": "An error occurred when creating pre-signed url for document reference",
    }

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
    RedirectClient = {
        "err_code": "LR_5001",
        "message": "Unsuccessful redirect",
    }

    """
       Errors for LoginException
    """
    LoginNoState = {
        "err_code": "LIN_4001",
        "message": "No auth err_code and/or state in the query string parameters",
    }
    LoginBadState = {
        "err_code": "LIN_4002",
        "message": "Unrecognised state value",
    }

    LoginBadAuth = {
        "err_code": "LIN_4003",
        "message": "Cannot log user in, expected information from CIS2 is missing",
    }
    LoginNoOrg = {
        "err_code": "LIN_4004",
        "message": "No org found for given ODS err_code",
    }
    LoginNullOrgs = {"err_code": "LIN_4005", "message": "No orgs found for user"}
    LoginNoRole = {
        "err_code": "LIN_4006",
        "message": "Unable to remove used state value",
    }
    LoginClient = {
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
    LoginNoSSM = {
        "err_code": "LIN_5005",
        "message": "SSM parameter values for GP admin/clinical or PCSE roles may not exist",
    }
    LoginAdminSSM = {
        "err_code": "LIN_5006",
        "message": "SSM parameter values for GP admin role may not exist",
    }
    LoginClinicalSSM = {
        "err_code": "LIN_5007",
        "message": "SSM parameter values for GP clinical user role may not exist",
    }
    LoginPcseSSM = {
        "err_code": "LIN_5008",
        "message": "SSM parameter values for PCSE user role may not exist",
    }
    LoginGpODS = {
        "err_code": "LIN_5009",
        "message": "SSM parameter values for GP organisation role code ma not exist",
    }
    LoginPcseODS = {
        "err_code": "LIN_5010",
        "message": "SSM parameter values for PSCE ODS code may not exist",
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
    StitchClient = {
        "err_code": "LGS_5002",
        "message": "Unable to return stitched pdf file due to internal error",
    }
    StitchDB = {
        "err_code": "LGS_5003",
        "message": "Unable to retrieve documents for patient",
    }
    StitchValidation = {
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
       Errors for Send Feedback lambda 
    """
    FeedbackMissingBody = {
        "err_code": "SFB_4001",
        "message": "Missing POST request body",
    }

    FeedbackInvalidBody = {
        "err_code": "SFB_4002",
        "message": "Invalid POST request body",
    }

    FeedbackSESFailure = {
        "err_code": "SFB_5001",
        "message": "Error occur when sending email by SES",
    }

    FeedbackFetchParamFailure = {
        "err_code": "SFB_5002",
        "message": "Failed to fetch parameters for sending email from SSM param store",
    }

    """
       Errors for Feature Flags lambda 
    """
    FeatureFlagNotFound = {
        "err_code": "FFL_4001",
        "message": "Feature flag/s may not exist in AppConfig profile",
    }

    FeatureFlagParseError = {
        "err_code": "FFL_5001",
        "message": "Failed to parse feature flag/s from AppConfig response",
    }

    FeatureFlagFailure = {
        "err_code": "FFL_5002",
        "message": "Failed to retrieve feature flag/s from AppConfig profile",
    }

    FeatureFlagDisabled = {
        "err_code": "FFL_5003",
        "message": "Feature is not enabled",
    }

    """
       Errors for Virus Scan lambda 
    """
    VirusScanNoBody = {"err_code": "VSR_4001", "message": "Missing event body"}
    VirusScanUnclean = {
        "err_code": "VSR_4002",
        "message": "Virus scanner failed",
    }
    VirusScanNoDocumentType = {
        "err_code": "VSR_4003",
        "message": "Document reference is missing a document type",
    }
    VirusScanTokenRequest = {
        "err_code": "VSR_5001",
        "message": "Virus scanner failed to fetch token",
    }
    VirusScanNoToken = {
        "err_code": "VSR_5002",
        "message": "Virus scanner failed to create new token",
    }
    VirusScanFailedRequest = {
        "err_code": "VSR_5003",
        "message": "Virus scanner failed request",
    }
    VirusScanAWSFailure = {
        "err_code": "VSR_5004",
        "message": "Error occurred with an AWS service",
    }

    """
       Errors for Upload Confirm Result lambda 
    """
    UploadConfirmResultMissingBody = {
        "err_code": "UC_4001",
        "message": "Missing POST request body",
    }
    UploadConfirmResultPayload = {
        "err_code": "UC_4002",
        "message": "Invalid json in body",
    }
    UploadConfirmResultProps = {
        "err_code": "UC_4003",
        "message": "Request body missing some properties",
    }
    UploadConfirmResultBadRequest = {
        "err_code": "UC_4004",
        "message": "Number of document references not equal to number of documents in dynamo table for this nhs number",
    }
    UploadConfirmResultAWSFailure = {
        "err_code": "UC_5004",
        "message": "Error occurred with an AWS service",
    }

    """
       Errors with no exception
    """
    DocDelNull = {
        "err_code": "DDS_4001",
        "message": "No records was found for given patient. No document deleted",
    }
    LoginNoAuth = {
        "err_code": "LIN_4007",
        "message": "No auth err_code and/or state in the query string parameters",
    }
    LogoutClient = {
        "err_code": "OUT_5001",
        "message": "Error logging user out",
    }
    LogoutDecode = {"err_code": "OUT_4001", "message": "Error while decoding JWT"}
    EnvMissing = {
        "err_code": "ENV_5001",
        "message": "An error occurred due to missing environment variable: '%(name)s'",
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
        "message": "Invalid patient number %(number)s",
    }
    PatientIdNoKey = {
        "err_code": "PN_4002",
        "message": "An error occurred due to missing key",
    }
    GatewayError = {
        "err_code": "GWY_5001",
        "message": "Failed to utilise AWS client/resource",
    }

    MockError = {
        "message": "Client error",
        "err_code": "AB_XXXX",
        "interaction_id": "88888888-4444-4444-4444-121212121212",
    }
