import { AxiosInstance } from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { UserAuth } from '../../types/blocks/userAuth';

export type AuthTokenArgs = {
    refreshToken: string;
    axios: AxiosInstance;
};

const getAuthRefresh = async ({ refreshToken, axios }: AuthTokenArgs) => {
    try {
        const { data } = await axios.get(endpoints.REFRESH_AUTH, {
            params: { refreshToken },
        });
        const userAuth: UserAuth = data;
        return userAuth;
    } catch (e) {
        throw e;
    }
};

export default getAuthRefresh;
