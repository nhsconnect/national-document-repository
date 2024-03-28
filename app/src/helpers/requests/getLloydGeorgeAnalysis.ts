import axios, { AxiosError } from 'axios';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
type Args = {
    baseUrl: string;
    baseHeaders: AuthHeaders;
    nhsNumber: number;
};
const getLloydGeorgeAnalysis = async ({ baseUrl, baseHeaders, nhsNumber }: Args) => {
    const gatewayUrl = baseUrl + endpoints.MEDICAL_ANALYSIS;

    try {
        const { data } = await axios.get(gatewayUrl, {
            headers: {
                ...baseHeaders,
            },
            params: {
                NhsNumber: nhsNumber,
            },
        });
        return data;
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default getLloydGeorgeAnalysis;
