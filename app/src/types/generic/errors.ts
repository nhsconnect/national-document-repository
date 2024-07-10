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
