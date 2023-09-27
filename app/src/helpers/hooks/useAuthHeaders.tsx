import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { AuthHeaders } from '../../types/blocks/authHeaders';

function useAuthHeaders() {
    const [session] = useSessionContext();
    const headers: AuthHeaders = {
        'Content-Type': 'application/json',
        authorizationToken: session.auth?.authorisation_token ?? '',
    };
    return headers;
}

export default useAuthHeaders;
