import React, { Dispatch, SetStateAction, useState } from 'react';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { BackLink, Card, Details } from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../../generic/pdfViewer/PdfViewer';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import LgRecordDetails from '../lgRecordDetails/LgRecordDetails';

export type Props = {
    patientDetails: PatientDetails;
    downloadStage: DOWNLOAD_STAGE;
    lloydGeorgeUrl: string;
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    stage: LG_RECORD_STAGE;
};
function LgRecordStage({
    patientDetails,
    downloadStage,
    lloydGeorgeUrl,
    lastUpdated,
    numberOfFiles,
    totalFileSizeInByte,
    setStage,
    stage,
}: Props) {
    const [fullScreen, setFullScreen] = useState(false);

    const dob: String = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const nhsNumber: String =
        patientDetails?.nhsNumber.slice(0, 3) +
        ' ' +
        patientDetails?.nhsNumber.slice(3, 6) +
        ' ' +
        patientDetails?.nhsNumber.slice(6, 10);

    const PdfCardDescription = () => {
        if (downloadStage === DOWNLOAD_STAGE.SUCCEEDED) {
            const detailsProps = {
                lastUpdated,
                numberOfFiles,
                totalFileSizeInByte,
                setStage,
            };

            return <LgRecordDetails {...detailsProps} setStage={setStage} stage={stage} />;
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
                    data-cy="back-link"
                    href="#"
                    onClick={() => {
                        setFullScreen(false);
                    }}
                >
                    Go back
                </BackLink>
            )}
            <div id="patient-info">
                <p style={{ marginBottom: 5, fontWeight: '700' }} data-cy="patient-name">
                    {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
                </p>
                <p style={{ fontSize: '16px', marginBottom: 5 }} data-cy="patient-nhs-number">
                    NHS number: {nhsNumber}
                </p>
                <p style={{ fontSize: '16px' }} data-cy="patient-dob">
                    Date of birth: {dob}
                </p>
            </div>
            {!fullScreen ? (
                <>
                    <Card style={{ marginBottom: 0 }}>
                        <Card.Content style={{ position: 'relative' }} data-cy="pdf-card">
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
                                <Details.Summary
                                    style={{ display: 'inline-block' }}
                                    data-cy="view-record-bin"
                                >
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
                                    data-cy="full-screen-btn"
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
