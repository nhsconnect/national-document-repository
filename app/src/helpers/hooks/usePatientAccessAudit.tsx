import { usePatientAccessAuditContext } from '../../providers/patientAccessAuditProvider/PatientAccessAuditProvider';

function usePatientAccessAudit() {
    const [patientAccessAudit] = usePatientAccessAuditContext();
    return patientAccessAudit;
}

export default usePatientAccessAudit;
