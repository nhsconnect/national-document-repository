export type FeatureFlags = {
    uploadLloydGeorgeWorkflowEnabled: boolean;
    uploadLambdaEnabled: boolean;
    uploadArfWorkflowEnabled: boolean;
};

export const defaultFeatureFlags = {
    uploadLloydGeorgeWorkflowEnabled: false,
    uploadLambdaEnabled: false,
    uploadArfWorkflowEnabled: false,
};
