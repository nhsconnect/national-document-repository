import { ErrorResponse } from './errorResponse';

class DownloadManifestError extends Error {
    response: { data: ErrorResponse };

    constructor(message: string) {
        super(message);
        this.name = 'DownloadManifestError';
        this.response = {
            data: {
                message,
                err_code: 'DMS_2001',
            },
        };
    }
}

export { DownloadManifestError };

class StitchRecordError extends Error {
    response: { data: ErrorResponse };

    constructor(message: string) {
        super(message);
        this.name = 'StitchRecordError';
        this.response = {
            data: {
                message,
                err_code: 'LGS_5000',
            },
        };
    }
}

export { StitchRecordError };
