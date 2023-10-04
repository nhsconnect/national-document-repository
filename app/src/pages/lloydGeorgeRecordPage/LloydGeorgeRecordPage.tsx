import React, { useEffect, useState } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import { Card, Details } from 'nhsuk-react-components';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import getLloydGeorgeRecord from '../../helpers/requests/lloydGeorgeSearchResult';
import PdfViewer from '../../components/generic/pdfViewer/PdfViewer';
import { getFormattedDatetime } from '../../helpers/utils/formatDatetime';
import { DOWNLOAD_STAGE } from '../../types/generic/downloadStage';
import formatFileSize from '../../helpers/utils/formatFileSize';

function LloydGeorgeRecordPage() {
    const [patientDetails] = usePatientDetailsContext();
    const [downloadStage, setDownloadStage] = useState(DOWNLOAD_STAGE.INITIAL);
    const [numberOfFiles, setNumberOfFiles] = useState(0);
    const [totalFileSizeInByte, setTotalFileSizeInByte] = useState(0);
    const [lastUpdated, setLastUpdated] = useState('');
    const [lloydGeorgeUrl, setLloydGeorgeUrl] = useState('');
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
            const search = async () => {
                setDownloadStage(DOWNLOAD_STAGE.PENDING);
                const nhsNumber: string = patientDetails?.nhsNumber || '';
                try {
                    const { number_of_files, total_file_size_in_byte, last_updated, presign_url } =
                        await getLloydGeorgeRecord({
                            nhsNumber,
                            baseUrl,
                        });
                    if (presign_url?.startsWith('https://')) {
                        setNumberOfFiles(number_of_files);
                        setLastUpdated(getFormattedDatetime(new Date(last_updated)));
                        setLloydGeorgeUrl(presign_url);
                        setDownloadStage(DOWNLOAD_STAGE.SUCCEEDED);
                        setTotalFileSizeInByte(total_file_size_in_byte);
                    }
                    setDownloadStage(DOWNLOAD_STAGE.SUCCEEDED);
                } catch (e) {
                    setDownloadStage(DOWNLOAD_STAGE.FAILED);
                }
            };
            void search();
        }
    }, [patientDetails, baseUrl, navigate]);

    const pdfCardDescription = (
        <>
            <p style={{ marginBottom: 16 }}>Last updated: {lastUpdated}</p>
            <p style={{ color: '#4C6272' }}>
                {numberOfFiles} files | File size: {formatFileSize(totalFileSizeInByte)} | File
                format: PDF
            </p>
        </>
    );
    const displayPdfCardDescription = () => {
        if (downloadStage === DOWNLOAD_STAGE.SUCCEEDED) {
            return pdfCardDescription;
        } else if (downloadStage === DOWNLOAD_STAGE.FAILED) {
            return <>No documents are available</>;
        } else {
            return <>Loading...</>;
        }
    };

    return (
        <>
            <>{patientInfo}</>
            <Card style={{ marginBottom: 0 }}>
                <Card.Content>
                    <Card.Heading style={{ fontWeight: '700', fontSize: '24px' }}>
                        Lloyd George record
                    </Card.Heading>
                    <Card.Description style={{ fontSize: '16px' }}>
                        {displayPdfCardDescription()}
                    </Card.Description>
                </Card.Content>
            </Card>
            {downloadStage === DOWNLOAD_STAGE.SUCCEEDED && (
                <Details expander open>
                    <Details.Summary>View record</Details.Summary>
                    <PdfViewer fileUrl={lloydGeorgeUrl} />
                </Details>
            )}
        </>
    );
}

export default LloydGeorgeRecordPage;
