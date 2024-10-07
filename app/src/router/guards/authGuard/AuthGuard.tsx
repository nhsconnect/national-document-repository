import { useEffect, type ReactNode, useState } from 'react';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';
import { routes } from '../../../types/generic/routes';
import { useLocation, useNavigate } from 'react-router-dom';

type Props = {
    children: ReactNode;
};

const INACTIVITY_TIMEOUT = 1 * 60 * 1000; // 1 minute

function AuthGuard({ children }: Props) {
    const [session, setSession] = useSessionContext();
    const navigate = useNavigate();
    const location = useLocation();
    const [lastActivity, setLastActivity] = useState(Date.now());

    useEffect(() => {
        const resetActivity = () => {
            console.log('ACTIVITY DETECTED');
            setLastActivity(Date.now());
        };

        const events = ['mousemove', 'keydown', 'click'];
        events.forEach((event) => window.addEventListener(event, resetActivity));

        const intervalId = setInterval(() => {
            if (Date.now() - lastActivity > INACTIVITY_TIMEOUT) {
                const searchParams = new URLSearchParams(location.search);
                searchParams.set('timeout', 'true');
                console.log('ACTIVITY NOT DETECTED');

                navigate({
                    pathname: routes.LOGOUT,
                    search: searchParams.toString(),
                });
            }
        }, 1000);

        if (!session.isLoggedIn) {
            navigate(routes.UNAUTHORISED);
        }
        return () => {
            events.forEach((event) => window.removeEventListener(event, resetActivity));
            clearInterval(intervalId);
        };
    }, [session, navigate, lastActivity, setSession, location.search]);

    return <>{children}</>;
}

export default AuthGuard;
