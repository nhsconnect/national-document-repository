import React, { Dispatch, SetStateAction, useState } from 'react';
import { BackLink, Card, Details, WarningCallout } from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../../generic/pdfViewer/PdfViewer';
import LloydGeorgeRecordDetails from '../lloydGeorgeRecordDetails/LloydGeorgeRecordDetails';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../helpers/hooks/usePatient';
import LloydGeorgeRecordError from '../lloydGeorgeRecordError/LloydGeorgeRecordError';
import useRole from '../../../helpers/hooks/useRole';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';

export type Props = {
    downloadStage: DOWNLOAD_STAGE;
    lloydGeorgeUrl: string;
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    stage: LG_RECORD_STAGE;
};

function LloydGeorgeRecordStage({
    downloadStage,
    lloydGeorgeUrl,
    lastUpdated,
    numberOfFiles,
    totalFileSizeInByte,
    setStage,
    stage,
}: Props) {
    const [fullScreen, setFullScreen] = useState(false);
    const patientDetails = usePatient();
    const dob: String = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const nhsNumber: string = patientDetails?.nhsNumber || '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);

    const role = useRole();
    // const [session] = useSessionContext();
    // const userIsGpAdminNonBsol = role === REPOSITORY_ROLE.GP_ADMIN && session.auth?.isBSOL;
    const userIsGpAdminNonBsol = true;

    const PdfCardDescription = () => {
        if (downloadStage === DOWNLOAD_STAGE.PENDING) {
            return <span> Loading...</span>;
        } else if (downloadStage === DOWNLOAD_STAGE.SUCCEEDED) {
            const detailsProps = {
                lastUpdated,
                numberOfFiles,
                totalFileSizeInByte,
                setStage,
                userIsGpAdminNonBsol,
            };
            return <LloydGeorgeRecordDetails {...detailsProps} />;
        } else {
            return <LloydGeorgeRecordError downloadStage={downloadStage} setStage={setStage} />;
        }
    };

    return (
        <div className="lloydgeorge_record-stage">
            {fullScreen && (
                <BackLink
                    data-testid="back-link"
                    href="#"
                    onClick={() => {
                        setFullScreen(false);
                    }}
                >
                    Go back
                </BackLink>
            )}
            {!fullScreen && userIsGpAdminNonBsol && (
                <div
                    id="gp-admin-non-bsol-lg"
                    className="lloydgeorge_record-stage_gp-admin-non-bsol"
                >
                    <WarningCallout id="close-page-warning">
                        <WarningCallout.Label headingLevel="h2">
                            Before downloading
                        </WarningCallout.Label>
                        <p>
                            If you download this record it removes from our storage. You will not be
                            able to access it here.
                        </p>
                        <p>
                            Once downloaded, you are responsible for this patient's information and
                            should follow data protection principles as outlined in UK General Data
                            Protection Regulation (GDPR).
                        </p>
                    </WarningCallout>
                    <h1>Available records</h1>
                </div>
            )}
            <div id="patient-info" className="lloydgeorge_record-stage_patient-info">
                <p data-testid="patient-name">
                    {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
                </p>
                <p data-testid="patient-nhs-number">NHS number: {formattedNhsNumber}</p>
                <p data-testid="patient-dob">Date of birth: {dob}</p>
            </div>
            {!fullScreen ? (
                <>
                    <Card className="lloydgeorge_record-stage_header">
                        <Card.Content
                            data-testid="pdf-card"
                            className="lloydgeorge_record-stage_header-content"
                        >
                            <Card.Heading className="lloydgeorge_record-stage_header-content-label">
                                Lloyd George record
                            </Card.Heading>
                            <PdfCardDescription />
                        </Card.Content>
                    </Card>
                    {downloadStage === DOWNLOAD_STAGE.SUCCEEDED && (
                        <>
                            <Details expander open className="lloydgeorge_record-stage_expander">
                                <Details.Summary
                                    style={{ display: 'inline-block' }}
                                    data-testid="view-record-bin"
                                >
                                    View record
                                </Details.Summary>
                                <button
                                    className="lloydgeorge_record-stage_expander-button link-button"
                                    data-testid="full-screen-btn"
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
        </div>
    );
}

export default LloydGeorgeRecordStage;
