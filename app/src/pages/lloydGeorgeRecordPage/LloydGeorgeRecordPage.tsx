import React, { useEffect, useState } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import { Card } from 'nhsuk-react-components';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import getLloydGeorgeRecord from '../../helpers/requests/lloydGeorgeSearchResult';

function LloydGeorgeRecordPage() {
    const [patientDetails] = usePatientDetailsContext();
    const [lloydGeorgeRecord, setLloydGeorgeRecord] = useState();
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();

    const dob = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const patientInfo = (
        <>
            <p style={{ fontSize: '24px', marginBottom: 5, fontWeight: '600' }}>
                {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
            </p>
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
        // search function that sets LG state based on request(to be created based on documentSearchResults request)
        // request will trigger lambda and either return pdf or null?
        // submission state from DocumentSearchResultsPage not needed?
        const search = async () => {
            const nhsNumber: string = patientDetails?.nhsNumber || '';

            const result = await getLloydGeorgeRecord({ nhsNumber, baseUrl });

            if (result.length > 0) {
                setLloydGeorgeRecord(result);
            }
        };
    }, [patientDetails, navigate]);

    return (
        <>
            <>{patientInfo}</>
            <Card>
                <Card.Content>
                    <Card.Heading>Lloyd George Record</Card.Heading>
                    <Card.Description>
                        {lloydGeorgeRecord ? 'display LG' : 'No documents are available'}
                    </Card.Description>
                </Card.Content>
            </Card>
        </>
    );
}

export default LloydGeorgeRecordPage;
