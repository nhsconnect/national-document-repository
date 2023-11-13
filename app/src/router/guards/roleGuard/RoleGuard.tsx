import { useEffect, type ReactNode } from 'react';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { useNavigate } from 'react-router';
import { useLocation } from 'react-router-dom';
import { routes } from '../../../types/generic/routes';
import { routeMap } from '../../AppRouter';

type Props = {
    children: ReactNode;
};

function RoleGuard({ children }: Props) {
    const role = REPOSITORY_ROLE.PCSE;
    const navigate = useNavigate();
    const location = useLocation();
    useEffect(() => {
        const routeKey = location.pathname as keyof typeof routeMap;
        const { unauthorized } = routeMap[routeKey];
        const denyResource = Array.isArray(unauthorized) && unauthorized.includes(role);
        console.log(unauthorized);
        console.log('DENY RESOURCE?:', denyResource);
        if (denyResource) {
            navigate(routes.UNAUTHORISED);
        }
    }, [role, location, navigate]);
    return <>{children}</>;
}

export default RoleGuard;
