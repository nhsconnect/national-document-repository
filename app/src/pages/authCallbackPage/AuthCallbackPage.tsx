import { useEffect } from 'react';
import getAuthToken, { AuthTokenArgs } from '../../helpers/requests/getAuthToken';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    useEffect(() => {
        const handleCallback = async (args: AuthTokenArgs) => {
            try {
                const { organisations, authorisation_token } = await getAuthToken(args);
            } catch (e) {}
            // Set Session
            // Navigate
        };

        const urlSearchParams = new URLSearchParams(window.location.search);
        const code = urlSearchParams.get('code');
        const state = urlSearchParams.get('state');
        if (code && state) {
            handleCallback({ baseUrl, code, state });
        }
    });

    return <div> CALLBACK WEEEE</div>;
};

export default AuthCallbackPage;
