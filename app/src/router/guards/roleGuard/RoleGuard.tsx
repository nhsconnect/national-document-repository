import { useEffect, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { routes } from '../../../types/generic/routes';
import { childRoutes, routeMap } from '../../AppRouter';
import useRole from '../../../helpers/hooks/useRole';

type Props = {
    children: ReactNode;
};

function RoleGuard({ children }: Props) {
    const role = useRole();
    const navigate = useNavigate();
    const location = useLocation();
    useEffect(() => {
        let routeKey = location.pathname;

        childRoutes.forEach((childRoute) => {
            if (childRoute.route === routeKey) {
                routeKey = childRoute.parent;
                return;
            }
        });

        const { unauthorized } = routeMap[routeKey as keyof typeof routeMap];
        const denyResource = Array.isArray(unauthorized) && role && unauthorized.includes(role);

        if (denyResource) {
            navigate(routes.UNAUTHORISED);
        }
    }, [role, location, navigate]);
    return <>{children}</>;
}

export default RoleGuard;
