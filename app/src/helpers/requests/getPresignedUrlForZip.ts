import axios from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { DOCUMENT_TYPE } from '../../types/pages/UploadDocumentsPage/types';
import { JOB_STATUS, PollingResponse } from '../../types/generic/downloadManifestJobStatus';

type Args = {
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
    docType?: DOCUMENT_TYPE;
    docReferences?: Array<string>;
};

type GetRequestArgs = {
    jobId: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type GetPresignedUrl = {
    data: string;
};

export const ThreePendingErrorMessage =
    'Document Manifest api call responded with "Pending" for 3 attempts.';

const getPresignedUrlForZip = async (args: Args) => {
    const { baseUrl, baseHeaders } = args;

    const jobId = await requestJobId(args);
    let pendingCount = 0;

    while (true) {
        const pollingResponse = await pollForPresignedUrl({
            baseUrl,
            baseHeaders,
            jobId,
        });

        switch (pollingResponse.status) {
            case JOB_STATUS.COMPLETED:
                return pollingResponse.url;
            case JOB_STATUS.PROCESSING:
                // wait for 10 sec
                break;
            case JOB_STATUS.PENDING:
                pendingCount += 1;

                if (pendingCount >= 3) {
                    throw new Error(ThreePendingErrorMessage);
                }
        }
    }
};

export const requestJobId = async ({
    nhsNumber,
    baseUrl,
    baseHeaders,
    docType = DOCUMENT_TYPE.ALL,
    docReferences,
}: Args): Promise<string> => {
    const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;

    const response = await axios.post(gatewayUrl, '', {
        headers: {
            ...baseHeaders,
        },
        params: {
            patientId: nhsNumber,
            docType: docType,
            ...(!!docReferences && { docReference: docReferences }),
        },
        paramsSerializer: { indexes: null },
    });

    return response.data.jobId;
};

export const pollForPresignedUrl = async ({
    jobId,
    baseUrl,
    baseHeaders,
}: GetRequestArgs): Promise<PollingResponse> => {
    const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;

    const { data } = await axios.get(gatewayUrl, {
        headers: {
            ...baseHeaders,
        },
        params: {
            jobId,
        },
    });

    return data;
};

export default getPresignedUrlForZip;
