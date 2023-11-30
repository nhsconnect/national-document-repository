import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';

function usePatient() {
    const [patient] = usePatientDetailsContext();
    return patient;
}

export default usePatient;
