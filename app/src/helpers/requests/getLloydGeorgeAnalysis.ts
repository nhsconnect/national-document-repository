import axios, { AxiosError } from 'axios';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
type Args = {
    baseUrl: string;
    baseHeaders: AuthHeaders;
};
const getLloydGeorgeAnalysis = async ({ baseUrl, baseHeaders }: Args) => {
    const gatewayUrl = baseUrl + endpoints.FEEDBACK;

    try {
        const { data } = await axios.get(gatewayUrl, {
            headers: {
                ...baseHeaders,
            },
            params: {
                fileId: 'random_text',
            },
        });
        return data;
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default getLloydGeorgeAnalysis;
