import { AxiosInstance } from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { UserAuth } from '../../types/blocks/userAuth';

export type AuthTokenArgs = {
    code: string;
    state: string;
    axios: AxiosInstance;
};

const getAuthToken = async ({ code, state, axios }: AuthTokenArgs) => {
    try {
        const { data } = await axios.get(endpoints.AUTH, {
            params: { code, state },
        });
        const userAuth: UserAuth = data;
        return userAuth;
    } catch (e) {
        throw e;
    }
};

export default getAuthToken;
