import { useEffect } from 'react';
import getAuthToken, { AuthTokenArgs } from '../../helpers/requests/getAuthToken';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { routes } from '../../types/generic/routes';
import { useNavigate } from 'react-router';
import Spinner from '../../components/generic/spinner/Spinner';
import { isMock } from '../../helpers/utils/isLocal';
import { AxiosError } from 'axios';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import { UserAuth } from '../../types/blocks/userAuth';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const [, setSession] = useSessionContext();
    const navigate = useNavigate();
    useEffect(() => {
        const handleError = (error: AxiosError) => {
            setSession({
                auth: null,
                isLoggedIn: false,
            });
            if (error.response?.status === 401) {
                navigate(routes.UNAUTHORISED_LOGIN);
            } else {
                navigate(routes.AUTH_ERROR);
            }
        };
        const handleSuccess = (auth: UserAuth) => {
            const { GP_ADMIN, GP_CLINICAL, PCSE } = REPOSITORY_ROLE;
            setSession({
                auth: auth,
                isLoggedIn: true,
            });

            if ([GP_ADMIN, GP_CLINICAL, PCSE].includes(auth.role)) {
                navigate(routes.HOME);
            } else {
                navigate(routes.AUTH_ERROR);
            }
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
                    handleError(error);
                }
            }
        };

        const urlSearchParams = new URLSearchParams(window.location.search);
        const code = urlSearchParams.get('code') ?? '';
        const state = urlSearchParams.get('state') ?? '';
        void handleCallback({ baseUrl, code, state });
    }, [baseUrl, setSession, navigate]);

    return <Spinner status="Logging in..." />;
};

export default AuthCallbackPage;
