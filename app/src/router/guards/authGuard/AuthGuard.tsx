import { useEffect, type ReactNode } from 'react';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router-dom';
type Props = {
    children: ReactNode;
};

function AuthGuard({ children }: Props) {
    const [session] = useSessionContext();
    const navigate = useNavigate();

    useEffect(() => {
        if (!session.isLoggedIn) {
            navigate(routes.UNAUTHORISED);
        }
    }, [session, navigate]);
    return <>{children}</>;
}

export default AuthGuard;
