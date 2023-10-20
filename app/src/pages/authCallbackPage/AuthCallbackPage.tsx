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
import { UserAuth } from '../../types/blocks/userAuth';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const [, setSession] = useSessionContext();
    const navigate = useNavigate();

    useEffect(() => {
        const handleError = () => {
            setSession({
                auth: null,
                isLoggedIn: false,
            });
            navigate(routes.AUTH_ERROR);
        };
        const handleSuccess = (auth: UserAuth) => {
            setSession({
                auth: auth,
                isLoggedIn: false,
            });
            navigate(routes.SELECT_ORG);
        };

        const handleCallback = async (args: AuthTokenArgs) => {
            try {
                const authData = await getAuthToken(args);
                handleSuccess(authData);
            } catch (e) {
                const error = e as AxiosError;
                if (isMock(error)) {
                    handleSuccess(buildUserAuth());
                } else {
                    handleError();
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
