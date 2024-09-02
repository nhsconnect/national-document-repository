import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { AuthHeaders } from '../../types/blocks/authHeaders';

function useBaseAPIHeaders(authHeaderName = 'Authorization') {
    const [session] = useSessionContext();
    const jwtToken = session.auth?.authorisation_token ?? '';
    const headers: AuthHeaders = {
        'Content-Type': 'application/json',
        [authHeaderName]: jwtToken,
        'X-Origin': typeof window !== 'undefined' ? window.location.href : '',
    };
    return headers;
}

export default useBaseAPIHeaders;
