import { useEffect, type ReactNode } from 'react';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { useNavigate } from 'react-router';
import { useLocation } from 'react-router-dom';

type Props = {
    children: ReactNode;
};

function RoleGuard({ children }: Props) {
    const role = REPOSITORY_ROLE.PCSE;
    const navigate = useNavigate();
    const location = useLocation();
    useEffect(() => {
        console.log(location.pathname);
        //     if (!patient) {
        //         navigate(routes.UNAUTHORISED);
        //     }
    }, [role, location]);
    return <>{children}</>;
}

export default RoleGuard;
