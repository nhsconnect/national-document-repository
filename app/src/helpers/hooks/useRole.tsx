import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';

function useRole() {
    const [session] = useSessionContext();

    if (!session.auth) {
        throw Error('Session context has not been set!');
    }

    return session.auth.role;
}

export default useRole;
