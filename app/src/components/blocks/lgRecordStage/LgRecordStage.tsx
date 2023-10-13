import React, { Dispatch, SetStateAction, useRef, useState } from 'react';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { BackLink, Card, Details } from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../../generic/pdfViewer/PdfViewer';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import { PdfActionLink } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { ReactComponent as Chevron } from '../../../styles/down-chevron.svg';
import { useOnClickOutside } from 'usehooks-ts';
import { Link } from 'react-router-dom';

type Props = {
    patientDetails: PatientDetails;
    downloadStage: DOWNLOAD_STAGE;
    lloydGeorgeUrl: string;
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    actionLinks: Array<PdfActionLink>;
    setShowActionsMenu: Dispatch<SetStateAction<boolean>>;
    showActionsMenu: boolean;
};

function LgRecordStage({
    patientDetails,
    downloadStage,
    lloydGeorgeUrl,
    lastUpdated,
    numberOfFiles,
    totalFileSizeInByte,
    showActionsMenu,
    setShowActionsMenu,
    actionLinks,
}: Props) {
    const [fullScreen, setFullScreen] = useState(false);
    const handleMoreActions = () => {
        setShowActionsMenu(!showActionsMenu);
    };

    const dob: String = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const nhsNumber: String =
        patientDetails?.nhsNumber.slice(0, 3) +
        ' ' +
        patientDetails?.nhsNumber.slice(3, 6) +
        ' ' +
        patientDetails?.nhsNumber.slice(6, 10);
    const actionsRef = useRef(null);
    useOnClickOutside(actionsRef, (e) => {
        setShowActionsMenu(false);
    });

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
                                            <Link
                                                to="#"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    link.handler();
                                                }}
                                            >
                                                {link.label}
                                            </Link>
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

    return (
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
            <>
                <p style={{ marginBottom: 5, fontWeight: '700' }}>
                    {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
                </p>
                <p style={{ fontSize: '16px', marginBottom: 5 }}>NHS number: {nhsNumber}</p>
                <p style={{ fontSize: '16px' }}>Date of birth: {dob}</p>
            </>
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
}

export default LgRecordStage;
