from enum import Enum


class FeatureFlags(Enum):
    NEMS_ENABLED = "nemsEnabled"
    UPLOAD_LLOYD_GEORGE_WORKFLOW_ENABLED = "uploadLloydGeorgeWorkflowEnabled"
    UPLOAD_LAMBDA_ENABLED = "uploadLambdaEnabled"
    UPLOAD_ARF_WORKFLOW_ENABLED = "uploadArfWorkflowEnabled"
    USE_SMARTCARD_AUTH = "useSmartcardAuth"
    LLOYD_GEORGE_VALIDATION_STRICT_MODE = "lloydGeorgeValidationStrictMode"
    ODS_REPORT_LAMBDA_ENABLED = "downloadOdsReportEnabled"
