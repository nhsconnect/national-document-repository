import { type ReactNode } from 'react';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { useNavigate } from 'react-router';
type Props = {
    children: ReactNode;
};

function RoleGuard({ children }: Props) {
    const role = REPOSITORY_ROLE.PCSE;
    const navigate = useNavigate();

    // useEffect(() => {
    //     if (!patient) {
    //         navigate(routes.UNAUTHORISED);
    //     }
    // }, [role, navigate]);
    return <>{children}</>;
}

export default RoleGuard;
