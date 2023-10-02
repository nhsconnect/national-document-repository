import React, { useEffect, useState } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import { Card, Details } from 'nhsuk-react-components';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import getLloydGeorgeRecord from '../../helpers/requests/lloydGeorgeSearchResult';
import PdfViewer from '../../components/generic/pdfViewer/PdfViewer';

function LloydGeorgeRecordPage() {
    const [patientDetails] = usePatientDetailsContext();
    const [lloydGeorgeRecord, setLloydGeorgeRecord] = useState(false);
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();

    const dob: String = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const nhsNumber: String =
        patientDetails?.nhsNumber.slice(0, 3) +
        ' ' +
        patientDetails?.nhsNumber.slice(3, 6) +
        ' ' +
        patientDetails?.nhsNumber.slice(6, 10);

    const patientInfo = (
        <>
            <p style={{ marginBottom: 5, fontWeight: '700' }}>
                {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
            </p>
            <p style={{ fontSize: '16px', marginBottom: 5 }}>NHS number: {nhsNumber}</p>
            <p style={{ fontSize: '16px' }}>Date of birth: {dob}</p>
        </>
    );

    useEffect(() => {
        if (!patientDetails) {
            navigate(routes.HOME);
        } else {
            // setLloydGeorgeRecord(true);
            const search = async () => {
                const nhsNumber: string = patientDetails?.nhsNumber || '';

                const result = await getLloydGeorgeRecord({ nhsNumber, baseUrl });

                if (result.length > 0) {
                    setLloydGeorgeRecord(result);
                }
            };
        }
    }, [patientDetails, navigate]);

    const pdfCardDescription = (
        <>
            <p style={{ marginBottom: 16 }}>Last updated: 'placeholder text'</p>
            <p style={{ color: '#4C6272' }}>'placeholder text'</p>
        </>
    );

    return (
        <>
            <>{patientInfo}</>
            <Card style={{ marginBottom: 0 }}>
                <Card.Content>
                    <Card.Heading style={{ fontWeight: '700', fontSize: '24px' }}>
                        Lloyd George record
                    </Card.Heading>
                    <Card.Description style={{ fontSize: '16px' }}>
                        {lloydGeorgeRecord ? pdfCardDescription : 'No documents are available'}
                    </Card.Description>
                </Card.Content>
            </Card>
            {lloydGeorgeRecord && (
                <Details expander open>
                    <Details.Summary>View record</Details.Summary>
                    <PdfViewer fileUrl="https://researchtorevenue.files.wordpress.com/2015/04/1r41ai10801601_fong.pdf" />
                </Details>
            )}
        </>
    );
}

export default LloydGeorgeRecordPage;
