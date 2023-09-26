import axios from 'axios';

type Args = {
    baseUrl: string;
    code: string;
    state: string;
};
const getAuthToken = async ({ baseUrl, code, state }: Args) => {
    const tokenResponse = await axios.get(`${baseUrl}/Auth/TokenRequest`, {
        params: { code, state },
    });
    console.log(tokenResponse);
};

export default getAuthToken;
