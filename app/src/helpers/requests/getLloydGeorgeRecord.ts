import axios from 'axios';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import waitForSeconds from '../utils/waitForSeconds';
import { JOB_STATUS } from '../../types/generic/downloadManifestJobStatus';
import { DownloadManifestError } from '../../types/generic/errors';
import { isRunningInCypress } from '../utils/isLocal';
export const DELAY_BETWEEN_POLLING_IN_SECONDS = isRunningInCypress() ? 0 : 10;

type Args = {
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

export type LloydGeorgeStitchResult = {
    jobStatus: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    lastUpdated: string;
    presignedUrl: string;
};

type GetRequestArgs = {
    jobId: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

const ThreePendingErrorMessage = 'Failed to initiate download';
const UnexpectedResponseMessage =
    'Got unexpected response from server when trying to download record';

async function getLloydGeorgeRecord(args: Args): Promise<LloydGeorgeStitchResult> {
    const { nhsNumber, baseUrl, baseHeaders } = args;

    const jobId = await requestJobId(args);
    let pendingCount = 0;

    while (pendingCount < 3) {
        await waitForSeconds(DELAY_BETWEEN_POLLING_IN_SECONDS);
        const pollingResponse = await pollForPresignedUrl({
            baseUrl,
            baseHeaders,
            jobId,
        });

        switch (pollingResponse?.jobStatus) {
            case JOB_STATUS.COMPLETED:
                return pollingResponse;
            case JOB_STATUS.PROCESSING:
                continue;
            case JOB_STATUS.PENDING:
                pendingCount += 1;
                continue;
            default:
                throw new DownloadManifestError(UnexpectedResponseMessage);
        }
    }
    throw new DownloadManifestError(ThreePendingErrorMessage);
}

export const requestJobId = async ({ nhsNumber, baseUrl, baseHeaders }: Args): Promise<string> => {
    const gatewayUrl = baseUrl + endpoints.LLOYDGEORGE_STITCH;

    const response = await axios.post(gatewayUrl, '', {
        headers: {
            ...baseHeaders,
        },
        params: {
            patientId: nhsNumber,
        },
    });

    return response.data.jobId;
};
export const pollForPresignedUrl = async ({
    jobId,
    baseUrl,
    baseHeaders,
}: GetRequestArgs): Promise<LloydGeorgeStitchResult> => {
    const gatewayUrl = baseUrl + endpoints.LLOYDGEORGE_STITCH;

    const { data } = await axios.get(gatewayUrl, {
        headers: {
            ...baseHeaders,
        },
        params: {
            jobId,
        },
    });
    if (!data.presignedUrl.startsWith('https://')) {
        return Promise.reject({ response: { status: 500 } });
    }

    return {
        ...data,
        presignedUrl: `${data.presignedUrl}&origin=${
            typeof window !== 'undefined' ? window.location.href : ''
        }`,
    };
};
export default getLloydGeorgeRecord;
