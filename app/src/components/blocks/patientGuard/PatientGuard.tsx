import { useEffect, type ReactNode } from 'react';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router';
import { usePatientDetailsContext } from '../../../providers/patientProvider/PatientProvider';
type Props = {
    children: ReactNode;
};

function PatientGuard({ children }: Props) {
    const [patient] = usePatientDetailsContext();
    const navigate = useNavigate();
    useEffect(() => {
        if (!patient) {
            navigate(routes.UNAUTHORISED);
        }
    }, [patient, navigate]);
    return <>{children}</>;
}

export default PatientGuard;
