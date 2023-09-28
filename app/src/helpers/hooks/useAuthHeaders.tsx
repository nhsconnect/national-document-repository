import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { AuthHeaders } from '../../types/blocks/authHeaders';

function useAuthHeaders() {
    const [session] = useSessionContext();
    const jwtToken = session.auth?.authorisation_token ?? '';
    const headers: AuthHeaders = {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${jwtToken}`,
    };
    return headers;
}

export default useAuthHeaders;
