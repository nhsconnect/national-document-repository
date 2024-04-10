const technicalIssueMsg = 'There is a technical issue on our side';
const accountVerifyMsg = 'There was an error verifying your account details';
const roleAccessMsg = 'There was an error verifying your role access';
const createFileMsg = 'There was problem when creating files for the patient';
const patientFileRetrievalMsg = 'There was an error retrieving files for the patient record';
const feedbackMsg = 'Your feedback failed to send';

const errorCodes: { [key: string]: string } = {
    CDR_5001: 'There was an unexplained error',
    CDR_5002: technicalIssueMsg,
    DT_5001: technicalIssueMsg,
    LR_5001: 'There is a problem with the server',
    LIN_5001: 'The details entered did not match',
    LIN_5002: 'There is an issue reaching the Care Identity Service (CIS)',
    LIN_5003: technicalIssueMsg,
    LIN_5004: 'There was an error responding to your request',
    LIN_5005: accountVerifyMsg,
    LIN_5006: accountVerifyMsg,
    LIN_5007: 'There was an error verifying your smartcard details',
    LIN_5008: roleAccessMsg,
    LIN_5009: roleAccessMsg,
    LIN_5010: accountVerifyMsg,
    DMS_5001: createFileMsg,
    DMS_5002: createFileMsg,
    DMS_5003: createFileMsg,
    LGS_5001: 'There was an error retrieving the patient record',
    LGS_5002: 'There was an error combining files for the patient record',
    LGS_5003: patientFileRetrievalMsg,
    LGS_5004: patientFileRetrievalMsg,
    DRS_5001: 'There was an error searching for patient files',
    DDS_5001: 'The files failed to delete',
    OUT_5001: 'There was a problem logging you out',
    ENV_5001: technicalIssueMsg,
    GWY_5001: technicalIssueMsg,
    SFB_5001: feedbackMsg,
    SFB_5002: feedbackMsg,
    FFL_5001: technicalIssueMsg,
    FFL_5002: technicalIssueMsg,
    FFL_5003: technicalIssueMsg,
    LGL_423: 'Record is uploading. Wait a few minutes and try again',
};

export default errorCodes;
