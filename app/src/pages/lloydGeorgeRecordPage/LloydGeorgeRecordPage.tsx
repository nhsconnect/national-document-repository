import React, { useEffect } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import { Card } from 'nhsuk-react-components';

function LloydGeorgeRecordPage() {
    const [patientDetails] = usePatientDetailsContext();
    const navigate = useNavigate();

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

    useEffect(() => {
        if (!patientDetails) {
            navigate(routes.HOME);
        }
    }, [patientDetails, navigate]);

    return (
        <>
            <>{patientInfo}</>
            <Card>
                <Card.Content>
                    <Card.Heading>Lloyd George Record</Card.Heading>
                    <Card.Description>No documents are available</Card.Description>
                </Card.Content>
            </Card>
        </>
    );
}

export default LloydGeorgeRecordPage;
