import React from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import { getFormattedDate } from '../../helpers/utils/formatDate';

function LloydGeorgeRecordPage() {
    const [patientDetails] = usePatientDetailsContext();

    const dob = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const patientInfo = (
        <>
            <p
                style={{ fontSize: '24px', marginBottom: 5, fontWeight: '600' }}
            >{`${patientDetails?.givenName} ${patientDetails?.familyName}`}</p>
            <p style={{ fontSize: '20px', marginBottom: 5 }}>
                NHS number: {patientDetails?.nhsNumber}
            </p>
            <p>{dob}</p>
        </>
    );

    return <>{patientInfo}</>;
}

export default LloydGeorgeRecordPage;
