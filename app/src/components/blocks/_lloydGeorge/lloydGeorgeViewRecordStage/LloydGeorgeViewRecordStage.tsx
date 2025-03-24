import { Dispatch, SetStateAction, useState } from 'react';
import { BackLink } from 'nhsuk-react-components';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import LloydGeorgeRecordDetails from '../lloydGeorgeRecordDetails/LloydGeorgeRecordDetails';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import LloydGeorgeRecordError from '../lloydGeorgeRecordError/LloydGeorgeRecordError';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';

import BackButton from '../../../generic/backButton/BackButton';
import { getUserRecordActionLinks } from '../../../../types/blocks/lloydGeorgeActions';
import RecordCard from '../../../generic/recordCard/RecordCard';
import useTitle from '../../../../helpers/hooks/useTitle';
import { routes, routeChildren } from '../../../../types/generic/routes';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';
import ProgressBar from '../../../generic/progressBar/ProgressBar';
import usePatient from '../../../../helpers/hooks/usePatient';

export type Props = {
    downloadStage: DOWNLOAD_STAGE;
    lastUpdated: string;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    stage: LG_RECORD_STAGE;
    refreshRecord: () => void;
    cloudFrontUrl: string;
    showMenu: boolean;
    resetDocState: () => void;
};

function LloydGeorgeViewRecordStage({
    downloadStage,
    lastUpdated,
    setStage,
    refreshRecord,
    cloudFrontUrl,
    showMenu,
    resetDocState,
}: Props) {
    const patientDetails = usePatient();
    const [fullScreen, setFullScreen] = useState(false);
    const role = useRole();
    const hasRecordInStorage = downloadStage === DOWNLOAD_STAGE.SUCCEEDED;
    const recordLinksToShow = getUserRecordActionLinks({ role, hasRecordInStorage });
    const recordDetailsProps: RecordDetailsProps = {
        downloadStage,
        lastUpdated,
    };

    const pageHeader = 'Available records';
    useTitle({ pageTitle: pageHeader });

    const menuClass = showMenu ? '--menu' : '--upload';

    return (
        <div className="lloydgeorge_record-stage">
            {fullScreen ? (
                <BackLink
                    data-testid="back-link"
                    href="#"
                    onClick={(e) => {
                        e.preventDefault();
                        setFullScreen(false);
                    }}
                >
                    Exit full screen
                </BackLink>
            ) : (
                <BackButton
                    dataTestid="go-back-button"
                    toLocation={
                        patientDetails?.deceased && role !== REPOSITORY_ROLE.PCSE
                            ? routeChildren.PATIENT_ACCESS_AUDIT_DECEASED
                            : routes.VERIFY_PATIENT
                    }
                    backLinkText="Go back"
                />
            )}

            <h1>{pageHeader}</h1>
            <PatientSimpleSummary showDeceasedTag />

            {!fullScreen ? (
                <div className="lloydgeorge_record-stage_flex">
                    <div
                        className={`lloydgeorge_record-stage_flex-row lloydgeorge_record-stage_flex-row${menuClass}`}
                    >
                        <RecordCard
                            heading="Lloyd George record"
                            fullScreenHandler={setFullScreen}
                            detailsElement={<RecordDetails {...recordDetailsProps} />}
                            isFullScreen={fullScreen}
                            refreshRecord={refreshRecord}
                            cloudFrontUrl={cloudFrontUrl}
                            resetDocStage={resetDocState}
                            recordLinks={recordLinksToShow}
                            setStage={setStage}
                            showMenu={showMenu}
                        />
                    </div>
                </div>
            ) : (
                <div className="lloydgeorge_record-stage_fs">
                    <RecordCard
                        heading="Lloyd George record"
                        fullScreenHandler={setFullScreen}
                        detailsElement={<RecordDetails {...recordDetailsProps} />}
                        isFullScreen={fullScreen}
                        refreshRecord={refreshRecord}
                        cloudFrontUrl={cloudFrontUrl}
                        resetDocStage={resetDocState}
                    />
                </div>
            )}
        </div>
    );
}

type RecordDetailsProps = Pick<Props, 'downloadStage' | 'lastUpdated'>;

const RecordDetails = ({ downloadStage, lastUpdated }: RecordDetailsProps) => {
    switch (downloadStage) {
        case DOWNLOAD_STAGE.INITIAL:
        case DOWNLOAD_STAGE.PENDING:
        case DOWNLOAD_STAGE.REFRESH:
            return <ProgressBar status="Loading..." />;
        case DOWNLOAD_STAGE.SUCCEEDED: {
            const detailsProps = {
                lastUpdated,
            };
            return <LloydGeorgeRecordDetails {...detailsProps} />;
        }
        default:
            return <LloydGeorgeRecordError downloadStage={downloadStage} />;
    }
};

export default LloydGeorgeViewRecordStage;
