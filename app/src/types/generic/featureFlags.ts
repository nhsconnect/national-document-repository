export type FeatureFlags = {
    nemsEnabled: boolean;
    uploadLloydGeorgeWorkflowEnabled: boolean;
    uploadLambdaEnabled: boolean;
    uploadArfWorkflowEnabled: boolean;
};

export const defaultFeatureFlags = {
    nemsEnabled: false,
    uploadLloydGeorgeWorkflowEnabled: false,
    uploadLambdaEnabled: false,
    uploadArfWorkflowEnabled: false,
};
