import { useEffect } from 'react';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { routes } from '../../types/generic/routes';
import { useNavigate } from 'react-router';
import Spinner from '../../components/generic/spinner/Spinner';
import { isMock } from '../../helpers/utils/isLocal';
import { AxiosError } from 'axios';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import logout, { Args } from '../../helpers/requests/logout';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const [session, setSession] = useSessionContext();
    const navigate = useNavigate();
    const baseHeaders = useBaseAPIHeaders('authorizationToken');

    useEffect(() => {
        const args: Args = { baseUrl, baseHeaders };

        const handleCallback = async (args: Args) => {
            try {
                await logout(args);
                setSession({
                    auth: null,
                    isLoggedIn: false,
                });
                navigate(routes.HOME);
            } catch (e) {
                const error = e as AxiosError;
                if (isMock(error)) {
                    setSession({
                        auth: null,
                        isLoggedIn: false,
                    });
                    navigate(routes.HOME);
                } else {
                    navigate(-1);
                }
            }
        };

        handleCallback(args);
    }, [baseUrl, setSession, navigate, baseHeaders]);

    return <Spinner status="Logging out..." />;
};

export default AuthCallbackPage;
