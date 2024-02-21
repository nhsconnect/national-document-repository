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
import getFeatureFlags from '../../helpers/requests/getFeatureFlags';
import { useFeatureFlagsContext } from '../../providers/featureFlagsProvider/FeatureFlagsProvider';
import { AuthHeaders } from '../../types/blocks/authHeaders';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const [, setSession] = useSessionContext();
    const [featureFlags, setFeatureFlags] = useFeatureFlagsContext();
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
        const handleSuccess = async (auth: UserAuth) => {
            const { GP_ADMIN, GP_CLINICAL, PCSE } = REPOSITORY_ROLE;
            setSession({
                auth: auth,
                isLoggedIn: true,
            });

            const jwtToken = auth?.authorisation_token ?? '';
            const baseHeaders: AuthHeaders = {
                'Content-Type': 'application/json',
                Authorization: jwtToken,
            };

            const featureFlagsData = await getFeatureFlags({ baseUrl, baseHeaders });
            setFeatureFlags({
                mockLocal: { ...featureFlags.mockLocal },
                appConfig: { ...featureFlagsData },
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
                    const { isBsol, userRole } = featureFlags.mockLocal;
                    await handleSuccess(buildUserAuth({ isBSOL: !!isBsol, role: userRole }));
                } else {
                    handleError(error);
                }
            }
        };

        const urlSearchParams = new URLSearchParams(window.location.search);
        const code = urlSearchParams.get('code') ?? '';
        const state = urlSearchParams.get('state') ?? '';
        void handleCallback({ baseUrl, code, state });
    }, [baseUrl, setSession, navigate, featureFlags]);

    return <Spinner status="Logging in..." />;
};

export default AuthCallbackPage;
