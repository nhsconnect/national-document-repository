import axios from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { UserAuth } from '../../types/blocks/userAuth';

export type AuthTokenArgs = {
    baseUrl: string;
    code: string;
    state: string;
};

const getAuthToken = async ({ baseUrl, code, state }: AuthTokenArgs) => {
    try {
        const tokenResponse: UserAuth = await axios.get(`${baseUrl}${endpoints.AUTH}`, {
            params: { code, state },
        });
        return tokenResponse;
    } catch (e) {
        throw e;
    }
};

export default getAuthToken;
