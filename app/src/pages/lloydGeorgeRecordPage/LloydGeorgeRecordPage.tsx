import React, { useEffect, useRef, useState } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import { getFormattedDate } from '../../helpers/utils/formatDate';
import { useNavigate } from 'react-router';
import { BackLink, Card, Details } from 'nhsuk-react-components';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import PdfViewer from '../../components/generic/pdfViewer/PdfViewer';
import { DOWNLOAD_STAGE } from '../../types/generic/downloadStage';
import formatFileSize from '../../helpers/utils/formatFileSize';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import { useOnClickOutside } from 'usehooks-ts';
import { ReactComponent as Chevron } from '../../styles/down-chevron.svg';
import { Link } from 'react-router-dom';
import { getFormattedDatetime } from '../../helpers/utils/formatDatetime';
import getLloydGeorgeRecord from '../../helpers/requests/getLloydGeorgeRecord';

enum LG_RECORD_STAGE {
    RECORD = 0,
    DOWNLOAD_ALL = 1,
}

function LloydGeorgeRecordPage() {
    const [patientDetails] = usePatientDetailsContext();
    const [downloadStage, setDownloadStage] = useState(DOWNLOAD_STAGE.INITIAL);
    const [numberOfFiles, setNumberOfFiles] = useState(0);
    const [totalFileSizeInByte, setTotalFileSizeInByte] = useState(0);
    const [lastUpdated, setLastUpdated] = useState('');
    const [lloydGeorgeUrl, setLloydGeorgeUrl] = useState('');
    const [fullScreen, setFullScreen] = useState(false);
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const mounted = useRef(false);
    const actionsRef = useRef(null);
    const [showActionsMenu, setShowActionsMenu] = useState(false);
    const [stage, setStage] = useState(LG_RECORD_STAGE.RECORD);

    useOnClickOutside(actionsRef, (e) => {
        setShowActionsMenu(false);
    });

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
    const handleMoreActions = () => {
        setShowActionsMenu(!showActionsMenu);
    };

    const downloadAllHandler = () => {
        setStage(LG_RECORD_STAGE.DOWNLOAD_ALL);
    };

    const actionLinks = [
        { label: 'See all files', handler: () => null },
        { label: 'Download all files', handler: downloadAllHandler },
        { label: 'Delete a selection of files', handler: () => null },
        { label: 'Delete file', handler: () => null },
    ];

    const PdfCardDetails = () => (
        <>
            <div>
                <div style={{ marginBottom: 16 }}>Last updated: {lastUpdated}</div>
                <div style={{ color: '#4C6272' }}>
                    {numberOfFiles} files | File size: {formatFileSize(totalFileSizeInByte)} | File
                    format: PDF
                </div>
            </div>
            <div className="lg-actions">
                <div
                    className={`nhsuk-select lg-actions-select ${
                        showActionsMenu ? 'lg-actions-select--selected' : ''
                    }`}
                    onClick={handleMoreActions}
                    style={{ background: '#fff' }}
                >
                    <div
                        className={`lg-actions-select_border ${
                            showActionsMenu ? 'lg-actions-select_border--selected' : ''
                        }`}
                    />
                    <span className="lg-actions-select_placeholder">Select an action...</span>
                    <Chevron className="lg-actions-select_icon" />
                </div>
                {showActionsMenu && (
                    <div ref={actionsRef}>
                        <Card className="lg-actions-menu">
                            <Card.Content>
                                <ol>
                                    {actionLinks.map((link, i) => (
                                        <li key={link.label + i}>
                                            <Link to="#">{link.label}</Link>
                                        </li>
                                    ))}
                                </ol>
                            </Card.Content>
                        </Card>
                    </div>
                )}
            </div>
        </>
    );
    const PdfCardDescription = () => {
        if (downloadStage === DOWNLOAD_STAGE.SUCCEEDED) {
            return <PdfCardDetails />;
        } else if (downloadStage === DOWNLOAD_STAGE.FAILED) {
            return <span>No documents are available</span>;
        } else {
            return <span> Loading...</span>;
        }
    };

    const RecordStage = () => (
        <>
            {fullScreen && (
                <BackLink
                    href="#"
                    onClick={() => {
                        setFullScreen(false);
                    }}
                >
                    Go back
                </BackLink>
            )}
            <>{patientInfo}</>
            {!fullScreen ? (
                <>
                    <Card style={{ marginBottom: 0 }}>
                        <Card.Content style={{ position: 'relative' }}>
                            <Card.Heading style={{ fontWeight: '700', fontSize: '24px' }}>
                                Lloyd George record
                            </Card.Heading>
                            <PdfCardDescription />
                        </Card.Content>
                    </Card>
                    {downloadStage === DOWNLOAD_STAGE.SUCCEEDED && (
                        <>
                            <Details
                                expander
                                open
                                style={{ position: 'relative', borderTop: 'none' }}
                            >
                                <Details.Summary style={{ display: 'inline-block' }}>
                                    View record
                                </Details.Summary>
                                <button
                                    style={{
                                        display: 'inline-block',
                                        position: 'absolute',
                                        right: '28px',
                                        top: '30px',
                                    }}
                                    className="link-button"
                                    onClick={() => {
                                        setFullScreen(true);
                                    }}
                                >
                                    View in full screen
                                </button>
                                <PdfViewer fileUrl={lloydGeorgeUrl} />
                            </Details>
                        </>
                    )}
                </>
            ) : (
                <PdfViewer fileUrl={lloydGeorgeUrl} />
            )}
        </>
    );
    const DownloadAllStage = () => (
        <>
            <h1>Downloading documents</h1>
            <h2>Alex Cool Bloggs</h2>
            <h3>NHS number: 1428571428</h3>
        </>
    );

    switch (stage) {
        case LG_RECORD_STAGE.RECORD:
            return <RecordStage />;
        case LG_RECORD_STAGE.DOWNLOAD_ALL:
            return <DownloadAllStage />;
    }
}

export default LloydGeorgeRecordPage;
