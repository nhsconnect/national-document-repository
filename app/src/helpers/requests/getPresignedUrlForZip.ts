import axios from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { DOCUMENT_TYPE } from '../../types/pages/UploadDocumentsPage/types';

type Args = {
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
    docType: DOCUMENT_TYPE;
};

type GetPresignedUrl = {
    data: string;
};

const getPresignedUrlForZip = async ({ nhsNumber, baseUrl, baseHeaders, docType }: Args) => {
    const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;

    const { data }: GetPresignedUrl = await axios.get(gatewayUrl, {
        headers: {
            ...baseHeaders,
        },
        params: {
            patientId: nhsNumber,
            docType,
        },
    });
    return data;
};

export default getPresignedUrlForZip;
