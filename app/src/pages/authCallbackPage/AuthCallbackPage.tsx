import { useEffect } from 'react';
import getAuthToken, { AuthTokenArgs } from '../../helpers/requests/getAuthToken';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { routes } from '../../types/generic/routes';
import { useNavigate } from 'react-router';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const [, setSession] = useSessionContext();
    const navigate = useNavigate();
    useEffect(() => {
        const handleCallback = async (args: AuthTokenArgs) => {
            try {
                const { organisations, authorisation_token } = await getAuthToken(args);
                setSession({
                    organisations,
                    authorisation_token,
                });
                navigate(routes.SELECT_ORG);
            } catch (e) {
                navigate(routes.HOME);
                console.error(e);
            }
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
