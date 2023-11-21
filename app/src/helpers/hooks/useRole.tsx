import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';

function useRole() {
    const [session] = useSessionContext();

    const role = session.auth ? session.auth.role : null;
    return role;
}

export default useRole;
