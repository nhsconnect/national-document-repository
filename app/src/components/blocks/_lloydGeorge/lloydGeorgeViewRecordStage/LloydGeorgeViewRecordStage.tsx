import { Dispatch, SetStateAction } from 'react';
import { Button, ChevronLeftIcon } from 'nhsuk-react-components';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import LloydGeorgeRecordDetails from '../lloydGeorgeRecordDetails/LloydGeorgeRecordDetails';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import LloydGeorgeRecordError from '../lloydGeorgeRecordError/LloydGeorgeRecordError';
import useRole from '../../../../helpers/hooks/useRole';
import BackButton from '../../../generic/backButton/BackButton';
import { getBSOLUserRecordActionLinks } from '../../../../types/blocks/lloydGeorgeActions';
import RecordCard from '../../../generic/recordCard/RecordCard';
import useTitle from '../../../../helpers/hooks/useTitle';
import { routes, routeChildren } from '../../../../types/generic/routes';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';
import ProgressBar from '../../../generic/progressBar/ProgressBar';
import usePatient from '../../../../helpers/hooks/usePatient';
import { useSessionContext } from '../../../../providers/sessionProvider/SessionProvider';
import RecordMenuCard from '../../../generic/recordMenuCard/RecordMenuCard';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';

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
    const [session, setUserSession] = useSessionContext();

    const role = useRole();

    const hasRecordInStorage = downloadStage === DOWNLOAD_STAGE.SUCCEEDED;

    const setFullScreen = (isFullscreen: boolean) => {
        setUserSession({ ...session, isFullscreen });

        if (isFullscreen) {
            if (document.fullscreenEnabled) {
                document.documentElement.requestFullscreen?.();
            }

            return;
        }

        document.exitFullscreen?.();
    };

    let recordLinksToShow = getBSOLUserRecordActionLinks({ role, hasRecordInStorage }).map(
        (link) => {
            link.onClick = () => {
                setFullScreen(false);
            };

            return link;
        },
    );

    const recordDetailsProps: RecordDetailsProps = {
        downloadStage,
        lastUpdated,
    };

    const pageHeader = 'Available records';
    useTitle({ pageTitle: pageHeader });

    const menuClass = showMenu ? '--menu' : '--upload';

    return (
        <div className="lloydgeorge_record-stage">
            {session.isFullscreen && (
                <div className="header">
                    <div className="header-items">
                        <Button
                            data-testid="back-link"
                            className="exit-fullscreen-button"
                            onClick={() => {
                                setFullScreen(false);
                            }}
                        >
                            <ChevronLeftIcon className="mr-2" />
                            Exit full screen
                        </Button>
                        <h1 className="title">Lloyd George record</h1>
                        <a
                            className="sign-out-link"
                            href={routes.LOGOUT}
                            onClick={() => {
                                setFullScreen(false);
                            }}
                        >
                            Sign out
                        </a>
                    </div>
                </div>
            )}

            <div className="main-content">
                <div className="top-info">
                    {!session.isFullscreen && (
                        <>
                            <BackButton
                                dataTestid="go-back-button"
                                toLocation={
                                    patientDetails?.deceased && role !== REPOSITORY_ROLE.PCSE
                                        ? routeChildren.PATIENT_ACCESS_AUDIT_DECEASED
                                        : routes.VERIFY_PATIENT
                                }
                                backLinkText="Go back"
                            />
                            <h1>{pageHeader}</h1>
                        </>
                    )}

                    <PatientSimpleSummary showDeceasedTag />

                    {session.isFullscreen && (
                        <RecordMenuCard
                            recordLinks={recordLinksToShow}
                            setStage={setStage}
                            showMenu={showMenu}
                        />
                    )}
                </div>

                {!session.isFullscreen ? (
                    <div className="lloydgeorge_record-stage_flex">
                        <div
                            className={`lloydgeorge_record-stage_flex-row lloydgeorge_record-stage_flex-row${menuClass}`}
                        >
                            <RecordCard
                                heading="Lloyd George record"
                                fullScreenHandler={setFullScreen}
                                detailsElement={<RecordDetails {...recordDetailsProps} />}
                                isFullScreen={session.isFullscreen!}
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
                    <RecordCard
                        heading="Lloyd George record"
                        fullScreenHandler={setFullScreen}
                        detailsElement={<RecordDetails {...recordDetailsProps} />}
                        isFullScreen={session.isFullscreen!}
                        refreshRecord={refreshRecord}
                        cloudFrontUrl={cloudFrontUrl}
                        resetDocStage={resetDocState}
                    />
                )}
            </div>
        </div>
    );
}

type RecordDetailsProps = Pick<Props, 'downloadStage' | 'lastUpdated'>;

const RecordDetails = ({ downloadStage, lastUpdated }: RecordDetailsProps) => {
    const [{ isFullscreen }] = useSessionContext();

    switch (downloadStage) {
        case DOWNLOAD_STAGE.INITIAL:
        case DOWNLOAD_STAGE.PENDING:
        case DOWNLOAD_STAGE.REFRESH:
            return <ProgressBar status="Loading..." className="loading-bar" />;

        case DOWNLOAD_STAGE.SUCCEEDED: {
            if (isFullscreen) {
                return <></>;
            }

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
