import { useEffect } from 'react';
import getAuthToken, { AuthTokenArgs } from '../../helpers/requests/getAuthToken';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { routes } from '../../types/generic/routes';
import { NavigateFunction, useNavigate } from 'react-router';
import Spinner from '../../components/generic/spinner/Spinner';
import { isMock } from '../../helpers/utils/isLocal';
import { AxiosError } from 'axios';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import { UserAuth } from '../../types/blocks/userAuth';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import NonBsolLandingPage from '../nonBsolLandingPage/NonBsolLandingPage';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const [session, setSession] = useSessionContext();
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
                isLoggedIn: true,
            });

            if (isBSOLOrPCSE(auth)) {
                continueToNextPage(auth, navigate);
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
                    handleError();
                }
            }
        };

        const urlSearchParams = new URLSearchParams(window.location.search);
        const code = urlSearchParams.get('code') ?? '';
        const state = urlSearchParams.get('state') ?? '';
        void handleCallback({ baseUrl, code, state });
    }, [baseUrl, setSession, navigate]);

    const confirmedAuth = session?.auth!;
    const shouldShowNonBSOLPage = confirmedAuth && !isBSOLOrPCSE(confirmedAuth);

    return shouldShowNonBSOLPage ? (
        <NonBsolLandingPage next={() => continueToNextPage(confirmedAuth, navigate)} />
    ) : (
        <Spinner status="Logging in..." />
    );
};

function isBSOLOrPCSE(auth: UserAuth): boolean {
    return auth.isBSOL || auth.role === REPOSITORY_ROLE.PCSE;
}

const continueToNextPage = (auth: UserAuth, navigate: NavigateFunction) => {
    if (!auth) {
        navigate(routes.AUTH_ERROR);
    }

    switch (auth.role) {
        case REPOSITORY_ROLE.GP_ADMIN:
            navigate(routes.UPLOAD_SEARCH);
            break;
        case REPOSITORY_ROLE.GP_CLINICAL:
            navigate(routes.UPLOAD_SEARCH);
            break;
        case REPOSITORY_ROLE.PCSE:
            navigate(routes.DOWNLOAD_SEARCH);
            break;
        default:
            navigate(routes.AUTH_ERROR);
            break;
    }
};

export default AuthCallbackPage;
