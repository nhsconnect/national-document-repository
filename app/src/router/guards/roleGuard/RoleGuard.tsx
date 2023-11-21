import { useEffect, type ReactNode } from 'react';
import { useNavigate } from 'react-router';
import { useLocation } from 'react-router-dom';
import { routes } from '../../../types/generic/routes';
import { routeMap } from '../../AppRouter';
import useRole from '../../../helpers/hooks/useRole';

type Props = {
    children: ReactNode;
};

function RoleGuard({ children }: Props) {
    const role = useRole();
    const navigate = useNavigate();
    const location = useLocation();
    useEffect(() => {
        const routeKey = location.pathname as keyof typeof routeMap;
        const { unauthorized } = routeMap[routeKey];
        const denyResource = Array.isArray(unauthorized) && unauthorized.includes(role);

        if (denyResource) {
            navigate(routes.UNAUTHORISED);
        }
    }, [role, location, navigate]);
    return <>{children}</>;
}

export default RoleGuard;
