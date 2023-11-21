import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { AuthHeaders } from '../../types/blocks/authHeaders';

function useBaseAPIHeaders(authHeaderName = 'Authorization') {
    const [session] = useSessionContext();
    const jwtToken = session.auth?.authorisation_token ?? '';

    if (!jwtToken) {
        throw Error('Session context has not been set!');
    }

    const headers: AuthHeaders = {
        'Content-Type': 'application/json',
        [authHeaderName]: jwtToken,
    };
    return headers;
}

export default useBaseAPIHeaders;
