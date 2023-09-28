import { useEffect, type ReactNode } from 'react';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router';
type Props = {
    children: ReactNode;
};

function AuthGuard({ children }: Props) {
    const [session] = useSessionContext();
    const navigate = useNavigate();
    useEffect(() => {
        if (!session.isLoggedIn) {
            console.log('AUTHGUARD ISNT FINDING A SESSION: ', session);
            navigate(routes.UNAUTHORISED);
        }
    }, [session, navigate]);
    return <>{children}</>;
}

export default AuthGuard;
