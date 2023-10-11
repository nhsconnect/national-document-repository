import React, { useEffect, useRef, useState } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import { useNavigate } from 'react-router';
import { Card, Details, Select } from 'nhsuk-react-components';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import getLloydGeorgeRecord from '../../helpers/requests/getLloydGeorgeRecord';
import PdfViewer from '../../components/generic/pdfViewer/PdfViewer';
import { getFormattedDatetime } from '../../helpers/utils/formatDatetime';
import { DOWNLOAD_STAGE } from '../../types/generic/downloadStage';
import formatFileSize from '../../helpers/utils/formatFileSize';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import { useOnClickOutside } from 'usehooks-ts';
import { ReactComponent as Chevron } from '../../styles/down-chevron.svg';

function LloydGeorgeRecordPage() {
    const [patientDetails] = usePatientDetailsContext();
    const [downloadStage, setDownloadStage] = useState(DOWNLOAD_STAGE.INITIAL);
    const [numberOfFiles, setNumberOfFiles] = useState(0);
    const [totalFileSizeInByte, setTotalFileSizeInByte] = useState(0);
    const [lastUpdated, setLastUpdated] = useState('');
    const [lloydGeorgeUrl, setLloydGeorgeUrl] = useState('');
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const mounted = useRef(false);
    const actionsRef = useRef(null);

    useOnClickOutside(actionsRef, () => setSelectExpanded(false));

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
        const search = async () => {
            setDownloadStage(DOWNLOAD_STAGE.PENDING);
            const nhsNumber: string = patientDetails?.nhsNumber || '';
            try {
                const { number_of_files, total_file_size_in_byte, last_updated, presign_url } =
                    await getLloydGeorgeRecord({
                        nhsNumber,
                        baseUrl,
                        baseHeaders,
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
            mounted.current = true;
        };
        if (!mounted.current) {
            void search();
        }
    }, [
        patientDetails,
        baseUrl,
        baseHeaders,
        navigate,
        setDownloadStage,
        setLloydGeorgeUrl,
        setLastUpdated,
        setNumberOfFiles,
        setTotalFileSizeInByte,
    ]);
    const [selectExpanded, setSelectExpanded] = useState(false);
    const pdfCardDescription = (
        <>
            <span style={{ marginBottom: 16 }}>Last updated: {lastUpdated}</span>
            <span style={{ color: '#4C6272' }}>
                {numberOfFiles} files | File size: {formatFileSize(totalFileSizeInByte)} | File
                format: PDF
            </span>
        </>
    );
    const displayPdfCardDescription = () => {
        if (downloadStage === DOWNLOAD_STAGE.SUCCEEDED) {
            return pdfCardDescription;
        } else if (downloadStage === DOWNLOAD_STAGE.FAILED) {
            return 'No documents are available';
        } else {
            return 'Loading...';
        }
    };

    const handleMoreActions = () => {
        setSelectExpanded(!selectExpanded);
    };

    return (
        //nhsuk-select--error
        <>
            <Select className="lg-test" label="More actions">
                <Select.Option>Select an action...</Select.Option>
            </Select>
            <div
                className={`nhsuk-select lg-actions-select ${
                    selectExpanded ? 'lg-actions-select--selected' : ''
                }`}
                ref={actionsRef}
                onClick={handleMoreActions}
                style={{ background: '#fff' }}
            >
                <div
                    className={`lg-actions-select_border ${
                        selectExpanded ? 'lg-actions-select_border--selected' : ''
                    }`}
                />
                <span className="lg-actions-select_placeholder">Select an action...</span>
                <Chevron className="lg-actions-select_icon" />
            </div>
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
