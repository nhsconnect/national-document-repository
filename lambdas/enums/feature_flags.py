from enum import Enum


class FeatureFlags(Enum):
    UPLOAD_LLOYD_GEORGE_WORKFLOW_ENABLED = "uploadLloydGeorgeWorkflowEnabled"
    UPLOAD_LAMBDA_ENABLED = "uploadLambdaEnabled"
    UPLOAD_ARF_WORKFLOW_ENABLED = "uploadArfWorkflowEnabled"
    USE_SMARTCARD_AUTH = "useSmartcardAuth"
    LLOYD_GEORGE_VALIDATION_STRICT_MODE_ENABLED = (
        "lloydGeorgeValidationStrictModeEnabled"
    )
