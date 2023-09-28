import { useEffect } from 'react';
import getAuthToken, { AuthTokenArgs } from '../../helpers/requests/getAuthToken';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { routes } from '../../types/generic/routes';
import { useNavigate } from 'react-router';
import Spinner from '../../components/generic/spinner/Spinner';
import { isMock } from '../../helpers/utils/isLocal';
import { AxiosError } from 'axios';
import { buildUserAuth } from '../../helpers/test/testBuilders';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const [session, setSession] = useSessionContext();
    const navigate = useNavigate();

    useEffect(() => {
        const handleCallback = async (args: AuthTokenArgs) => {
            try {
                const authResponse = await getAuthToken(args);
                setSession({
                    auth: authResponse,
                    isLoggedIn: false,
                });
                navigate(routes.SELECT_ORG);
            } catch (e) {
                const error = e as AxiosError;
                if (isMock(error)) {
                    setSession({
                        auth: buildUserAuth(),
                        isLoggedIn: false,
                    });
                    navigate(routes.SELECT_ORG);
                } else {
                    navigate(routes.HOME);
                    console.error(e);
                }
            }
        };

        const urlSearchParams = new URLSearchParams(window.location.search);
        const code = urlSearchParams.get('code') ?? '';
        const state = urlSearchParams.get('state') ?? '';
        handleCallback({ baseUrl, code, state });
    }, [baseUrl, setSession, navigate]);

    return <Spinner status="Logging in..." />;
};

export default AuthCallbackPage;
