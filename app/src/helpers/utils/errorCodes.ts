const errorCodes: { [key: string]: string } = {
    CDR_5001: 'Internal error',
    CDR_5002: 'Internal error',
    DT_5001: 'Failed to resolve dynamodb table name for this document',
    LR_5001: 'Server error',
    LIN_5001: 'Unrecognised state value',
    LIN_5002: 'Issue when contacting CIS2',
    LIN_5003: 'Bad response from ODS API',
    LIN_5004: 'Unable to remove used state value',
    LIN_5005: 'Failed to find SSM parameter value for user role',
    LIN_5006: 'Failed to find SSM parameter value for user role',
    LIN_5007: 'Failed to find SSM parameter value for smartcard',
    LIN_5008: 'Failed to find SSM parameter value for PCSE role',
    LIN_5009: 'Failed to find SSM parameter value for GP role',
    LIN_5010: 'SSM parameter values for PSCE ODS err_code may not exist',
    DMS_5001: 'Failed to parse document reference from from DynamoDb response',
    DMS_5002: 'Failed to create document manifest',
    DMS_5003: 'Failed to create document manifest',
    LGS_5001: 'Unable to retrieve documents for patient',
    LGS_5002: 'Unable to return stitched pdf file due to internal error',
    LGS_5003: 'Unable to retrieve documents for patient',
    LGS_5004: 'Unable to retrieve documents for patient',
    DRS_5001: 'An error occurred when searching for available documents',
    DDS_5001: 'Failed to delete documents',
    OUT_5001: 'Error logging user out',
    ENV_5001: 'An error occurred due to missing environment variable',
    GWY_5001: 'Failed to utilise AWS client/resource',
    SFB_5001: 'Error occur when sending email by SES',
    SFB_5002: 'Failed to fetch parameters for sending email from SSM param store',
    FFL_5001: 'Failed to parse feature flag/s from AppConfig response',
    FFL_5002: 'Failed to retrieve feature flag/s from AppConfig profile',
    FFL_5003: 'Feature is not enabled',
    LGL_423: 'Record is uploading. Wait a few minutes and try again.',
};

export default errorCodes;
