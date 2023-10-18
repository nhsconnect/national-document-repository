import axios from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { AuthHeaders } from '../../types/blocks/authHeaders';

type Args = {
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type GetPresignedUrl = {
    data: string;
};

const getPresignedUrlForZip = async ({ nhsNumber, baseUrl, baseHeaders }: Args) => {
    const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;

    const { data }: GetPresignedUrl = await axios.get(gatewayUrl, {
        headers: {
            ...baseHeaders,
        },
        params: {
            patientId: nhsNumber,
            docType: 'ARF',
        },
    });
    return data;
};

export default getPresignedUrlForZip;
