import axios from 'axios';
import { endpoints } from '../../types/generic/endpoints';
type Args = {
    baseUrl: string;
    code: string;
    state: string;
};
const getAuthToken = async ({ baseUrl, code, state }: Args) => {
    const tokenResponse = await axios.get(`${baseUrl}${endpoints.AUTH}`, {
        params: { code, state },
    });
    console.log(tokenResponse);
};

export default getAuthToken;
