import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';

function usePatient() {
    const [patient] = usePatientDetailsContext();

    if (!patient) {
        throw Error('Patient context has not been set!');
    }

    return patient;
}

export default usePatient;
