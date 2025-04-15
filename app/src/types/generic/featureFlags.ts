export type FeatureFlags = {
    uploadLloydGeorgeWorkflowEnabled: boolean;
    uploadLambdaEnabled: boolean;
    uploadArfWorkflowEnabled: boolean;
};

export const defaultFeatureFlags: FeatureFlags = {
    uploadLloydGeorgeWorkflowEnabled: false,
    uploadLambdaEnabled: false,
    uploadArfWorkflowEnabled: false,
};
