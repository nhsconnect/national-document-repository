export type UploadSession = {
    [key: string]: S3Upload;
};

export type S3Upload = {
    url: string;
    fields: S3UploadFields;
};

export type S3UploadFields = {
    key: string;
    'x-amz-algorithm': string;
    'x-amz-credential': string;
    'x-amz-date': string;
    'x-amz-security-token': string;
    policy: string;
    'x-amz-signature': string;
};
