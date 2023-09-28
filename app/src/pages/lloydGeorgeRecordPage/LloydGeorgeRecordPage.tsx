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
        setLloydGeorgeRecord(true);
        // const search = async () => {
        //     const nhsNumber: string = patientDetails?.nhsNumber || '';
        //
        //     const result = await getLloydGeorgeRecord({ nhsNumber, baseUrl });
        //
        //     if (result.length > 0) {
        //         setLloydGeorgeRecord(result);
        //     }
        // };
    }, [patientDetails, navigate]);

    return (
        <>
            <>{patientInfo}</>
            <Card style={{ marginBottom: 0 }}>
                <Card.Content>
                    <Card.Heading>Lloyd George Record</Card.Heading>
                    <Card.Description>
                        {lloydGeorgeRecord
                            ? 'display LG details and pdf'
                            : 'No documents are available'}
                    </Card.Description>
                </Card.Content>
            </Card>
            {lloydGeorgeRecord && (
                <Details expander>
                    <Details.Summary>View record</Details.Summary>
                    <PdfViewer fileUrl="https://researchtorevenue.files.wordpress.com/2015/04/1r41ai10801601_fong.pdf" />
                </Details>
            )}
        </>
    );
}

export default LloydGeorgeRecordPage;
