import { useEffect, type ReactNode, useRef } from 'react';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';
import { routes } from '../../../types/generic/routes';
import { useLocation, useNavigate } from 'react-router-dom';

type Props = {
    children: ReactNode;
};

const TIMEOUT_MINUTES = 0.5;

function AuthGuard({ children }: Props) {
    const [session] = useSessionContext();
    const navigate = useNavigate();
    const location = useLocation();
    const lastActivityRef = useRef(Date.now());
    const intervalIdRef = useRef<number | null>(null);

    // Check user is logged in on every child page load
    useEffect(() => {
        if (!session.isLoggedIn) {
            navigate(routes.UNAUTHORISED);
        }
    }, [session, navigate]);

    // Attach event listeners for user active
    useEffect(() => {
        const resetActivity = () => {
            console.log('user activity');
            lastActivityRef.current = Date.now();
        };

        const events = ['mousemove', 'keydown', 'click'];
        events.forEach((event) => window.addEventListener(event, resetActivity));

        return () => {
            events.forEach((event) => window.removeEventListener(event, resetActivity));
        };
    }, []);

    // Attach event listener for user inactive
    useEffect(() => {
        const inactiveTimeout = TIMEOUT_MINUTES * 60 * 1000;
        const checkInactivity = () => {
            if (Date.now() - lastActivityRef.current > inactiveTimeout) {
                const searchParams = new URLSearchParams(location.search);
                searchParams.set('timeout', 'true');
                console.log('user inactive');
                navigate({
                    pathname: routes.LOGOUT,
                    search: searchParams.toString(),
                });
            }
        };

        intervalIdRef.current = window.setInterval(checkInactivity, 1000);
        return () => {
            if (intervalIdRef.current) {
                clearInterval(intervalIdRef.current);
            }
        };
    }, [navigate, location.search]);

    return <>{children}</>;
}

export default AuthGuard;
