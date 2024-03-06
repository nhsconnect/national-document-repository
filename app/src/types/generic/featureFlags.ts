export type FeatureFlags = {
    uploadLloydGeorgeWorkflowEnabled: boolean;
    uploadLambdaEnabled: boolean;
    uploadArfWorkflowEnabled: boolean;
};

export const defaultFeatureFlags = {
    uploadLloydGeorgeWorkflowEnabled: true,
    uploadLambdaEnabled: true,
    uploadArfWorkflowEnabled: false,
};
