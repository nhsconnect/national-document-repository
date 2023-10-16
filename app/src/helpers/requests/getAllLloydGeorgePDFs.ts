import { AxiosError } from 'axios';
import axios from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { AuthHeaders } from '../../types/blocks/authHeaders';

type Args = {
    baseUrl: string;
    baseHeaders: AuthHeaders;
    nhsNumber: string;
};

const getAllLloydGeorgePDFs = async ({ baseUrl, baseHeaders, nhsNumber }: Args) => {
    const gatewayUrl = baseUrl + endpoints.LG_STITCH;
    try {
        const response = await axios.get(gatewayUrl, {
            headers: {
                ...baseHeaders,
            },
            params: {
                patientId: nhsNumber,
            },
        });
        return response;
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default getAllLloydGeorgePDFs;
