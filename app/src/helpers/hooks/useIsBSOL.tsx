import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';

function useIsBSOL() {
    const [session] = useSessionContext();

    const isBSOL = session.auth ? session.auth.isBSOL : null;
    return isBSOL;
}

export default useIsBSOL;
