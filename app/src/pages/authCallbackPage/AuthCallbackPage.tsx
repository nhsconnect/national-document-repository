import { useEffect, useState } from 'react';
import getAuthToken, { AuthTokenArgs } from '../../helpers/requests/getAuthToken';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { routes } from '../../types/generic/routes';
import { useNavigate } from 'react-router';
import Spinner from '../../components/generic/spinner/Spinner';
import { isMock } from '../../helpers/utils/isLocal';
import { AxiosError } from 'axios';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import { UserAuth } from '../../types/blocks/userAuth';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';

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
                isLoggedIn: true,
            });

            const nextPage = searchPatientPageByUserRole(auth);
            navigate(nextPage);
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

    return <Spinner status="Logging in..." />;
};

const searchPatientPageByUserRole = (auth: UserAuth): routes => {
    switch (auth?.role) {
        case REPOSITORY_ROLE.GP_ADMIN:
            return auth.isBSOL ? routes.UPLOAD_SEARCH : routes.NON_BSOL_LANDING;
        case REPOSITORY_ROLE.GP_CLINICAL:
            return routes.UPLOAD_SEARCH;
        case REPOSITORY_ROLE.PCSE:
            return routes.DOWNLOAD_SEARCH;
        default:
            return routes.AUTH_ERROR;
    }
};

export default AuthCallbackPage;
