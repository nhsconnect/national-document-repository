import axios from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { DOCUMENT_TYPE } from '../../types/pages/UploadDocumentsPage/types';

type Args = {
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
    docType?: DOCUMENT_TYPE;
    docReferences?: Array<string>;
};

type GetRequestArgs = {
    jobId: string;
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type GetPresignedUrl = {
    data: string;
};

const getPresignedUrlForZip = async ({
    nhsNumber,
    baseUrl,
    baseHeaders,
    docType = DOCUMENT_TYPE.ALL,
    docReferences,
}: Args) => {
    const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;

    const { data }: GetPresignedUrl = await axios.get(gatewayUrl, {
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
    return data;
};

export const requestJobId = async ({
    nhsNumber,
    baseUrl,
    baseHeaders,
    docType = DOCUMENT_TYPE.ALL,
    docReferences,
}: Args) => {
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

export const pollForPresignedUrl = async ({ baseUrl }: GetRequestArgs) => {
    const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;

    const { data } = await axios.get(gatewayUrl);

    return data;
};

export default getPresignedUrlForZip;
