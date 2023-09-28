import { useEffect } from 'react';
import getAuthToken, { AuthTokenArgs } from '../../helpers/requests/getAuthToken';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { routes } from '../../types/generic/routes';
import { useNavigate } from 'react-router';
import Spinner from '../../components/generic/spinner/Spinner';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const [session, setSession] = useSessionContext();
    const navigate = useNavigate();
    useEffect(() => {
        const handleCallback = async (args: AuthTokenArgs) => {
            try {
                const { organisations, authorisation_token } = await getAuthToken(args);
                setSession({
                    organisations,
                    authorisation_token,
                });
                setTimeout(() => {
                    window.alert(JSON.stringify(session));
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

    return <Spinner status="Logging in..." />;
};

export default AuthCallbackPage;
