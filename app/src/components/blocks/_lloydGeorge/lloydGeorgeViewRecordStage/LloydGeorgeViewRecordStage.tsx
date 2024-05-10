import React, { Dispatch, SetStateAction, useState } from 'react';
import {
    BackLink,
    Button,
    Checkboxes,
    Fieldset,
    InsetText,
    WarningCallout,
} from 'nhsuk-react-components';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import PdfViewer from '../../../generic/pdfViewer/PdfViewer';
import LloydGeorgeRecordDetails from '../lloydGeorgeRecordDetails/LloydGeorgeRecordDetails';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../../helpers/hooks/usePatient';
import LloydGeorgeRecordError from '../lloydGeorgeRecordError/LloydGeorgeRecordError';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import useIsBSOL from '../../../../helpers/hooks/useIsBSOL';
import WarningText from '../../../generic/warningText/WarningText';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import { useForm } from 'react-hook-form';
import { InputRef } from '../../../../types/generic/inputRef';
import BackButton from '../../../generic/backButton/BackButton';
import {
    getBSOLUserRecordActionLinks,
    getNonBSOLUserRecordActionLinks,
} from '../../../../types/blocks/lloydGeorgeActions';
import RecordCard from '../../../generic/recordCard/RecordCard';
import RecordMenuCard from '../../../generic/recordMenuCard/RecordMenuCard';
import useTitle from '../../../../helpers/hooks/useTitle';
import PatientSummary from '../../../generic/patientSummary/PatientSummary';
import ProgressBar from '../../../generic/progressBar/ProgressBar';

export type Props = {
    downloadStage: DOWNLOAD_STAGE;
    lloydGeorgeUrl: string;
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    stage: LG_RECORD_STAGE;
};

function LloydGeorgeViewRecordStage({
    downloadStage,
    lloydGeorgeUrl,
    lastUpdated,
    numberOfFiles,
    totalFileSizeInByte,
    setStage,
}: Props) {
    const [fullScreen, setFullScreen] = useState(false);
    const [downloadRemoveButtonClicked, setDownloadRemoveButtonClicked] = useState(false);
    const patientDetails = usePatient();
    const dob: string = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';
    const { register, handleSubmit, formState, clearErrors, setError, setFocus } = useForm({
        reValidateMode: 'onSubmit',
    });
    const { ref: inputRef, ...checkboxProps } = register('confirmDownloadRemove', {
        required: true,
    });

    const handleDownloadAndRemoveRecordButton = () => {
        if (downloadRemoveButtonClicked) {
            setError('confirmDownloadRemove', { type: 'custom', message: 'true' });
        }
        setFocus('confirmDownloadRemove');
        setDownloadRemoveButtonClicked(true);
    };

    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);

    const role = useRole();
    const isBSOL = useIsBSOL();
    const userIsGpAdminNonBSOL = role === REPOSITORY_ROLE.GP_ADMIN && !isBSOL;

    const hasRecordInStorage = downloadStage === DOWNLOAD_STAGE.SUCCEEDED;

    const recordLinksToShow = isBSOL
        ? getBSOLUserRecordActionLinks({ role, hasRecordInStorage })
        : getNonBSOLUserRecordActionLinks({
              role,
              hasRecordInStorage,
              onClickFunctionForDownloadAndRemove: handleDownloadAndRemoveRecordButton,
          });
    const showMenu = recordLinksToShow.length > 0;

    const handleConfirmDownloadAndRemoveButton = () => {
        setStage(LG_RECORD_STAGE.DOWNLOAD_ALL);
    };
    const handleCancelButton = () => {
        setDownloadRemoveButtonClicked(false);
        clearErrors('confirmDownloadRemove');
    };

    const RecordDetails = () => {
        if (downloadStage === DOWNLOAD_STAGE.PENDING) {
            return <ProgressBar status="Loading..." />;
        } else if (downloadStage === DOWNLOAD_STAGE.SUCCEEDED) {
            const detailsProps = {
                lastUpdated,
                numberOfFiles,
                totalFileSizeInByte,
            };
            return <LloydGeorgeRecordDetails {...detailsProps} />;
        } else {
            return <LloydGeorgeRecordError downloadStage={downloadStage} setStage={setStage} />;
        }
    };

    const pageHeader = 'Available records';
    useTitle({ pageTitle: pageHeader });

    return (
        <div className="lloydgeorge_record-stage">
            {formState.errors.confirmDownloadRemove && (
                <ErrorBox
                    dataTestId="confirm-download-and-remove-error"
                    errorBoxSummaryId="confirm-download-and-remove"
                    messageTitle="There is a problem"
                    errorBody="You must confirm if you want to download and remove this record"
                />
            )}
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
                <BackButton />
            )}
            {!fullScreen && userIsGpAdminNonBSOL && (
                <div className="lloydgeorge_record-stage_gp-admin-non-bsol">
                    <WarningCallout
                        id="before-downloading-warning"
                        data-testid="before-downloading-warning"
                    >
                        <WarningCallout.Label headingLevel="h2">
                            Before downloading
                        </WarningCallout.Label>
                        <p>
                            If you download this record it will be removed from our storage. You
                            will not be able to access it here.
                        </p>
                        <p>
                            Once downloaded, it is your responsibility to keep this patient’s
                            information safe. You must store the record securely, and ensure it’s
                            transferred safely to other practices if the patient moves.
                        </p>
                        {downloadRemoveButtonClicked && (
                            <InsetText className="lloydgeorge_record-stage_gp-admin-non-bsol_inset-text">
                                <form
                                    onSubmit={handleSubmit(handleConfirmDownloadAndRemoveButton)}
                                    className={
                                        formState.errors.confirmDownloadRemove
                                            ? 'nhsuk-form-group--error'
                                            : 'nhsuk-form-group'
                                    }
                                >
                                    <Fieldset aria-describedby="waste-hint">
                                        <h4>
                                            Are you sure you want to download and remove this
                                            record?
                                        </h4>
                                        <WarningText
                                            text="If you download this record, it removes from our storage.
                                            You must keep the patient's record safe."
                                        />
                                        <Checkboxes
                                            data-testid="confirm-download-and-remove-checkbox"
                                            className="lloydgeorge_record-stage_gp-admin-non-bsol_inset-text_checkbox"
                                            name="confirm-download-remove"
                                            id="confirm-download-remove"
                                            error={
                                                formState.errors.confirmDownloadRemove
                                                    ? 'Confirm if you want to download and remove this record'
                                                    : undefined
                                            }
                                        >
                                            <Checkboxes.Box
                                                value="confirm-download-remove"
                                                inputRef={inputRef as InputRef}
                                                {...checkboxProps}
                                            >
                                                I understand that downloading this record removes it
                                                from storage.
                                            </Checkboxes.Box>
                                        </Checkboxes>
                                    </Fieldset>
                                    <Button
                                        data-testid="confirm-download-and-remove-btn"
                                        type="submit"
                                        id="confirm-download-remove"
                                        className="lloydgeorge_record-stage_gp-admin-non-bsol_inset-text_confirm-download-remove-button"
                                    >
                                        Yes, download and remove
                                    </Button>
                                    <Button
                                        onClick={handleCancelButton}
                                        className="nhsuk-button nhsuk-button--secondary"
                                        style={{ marginLeft: 30 }}
                                    >
                                        Cancel
                                    </Button>
                                </form>
                            </InsetText>
                        )}
                    </WarningCallout>
                </div>
            )}

            <h1>{pageHeader}</h1>
            <PatientSummary />
            {!fullScreen ? (
                <>
                    {showMenu ? (
                        <div className="lloydgeorge_record-stage_flex">
                            <div className="lloydgeorge_record-stage_flex-row">
                                <RecordMenuCard
                                    recordLinks={recordLinksToShow}
                                    setStage={setStage}
                                />
                            </div>
                            <div className="lloydgeorge_record-stage_flex-row">
                                <RecordCard
                                    downloadStage={downloadStage}
                                    recordUrl={lloydGeorgeUrl}
                                    heading="Lloyd George record"
                                    fullScreenHandler={setFullScreen}
                                    detailsElement={<RecordDetails />}
                                />
                            </div>
                        </div>
                    ) : (
                        <RecordCard
                            downloadStage={downloadStage}
                            recordUrl={lloydGeorgeUrl}
                            heading="Lloyd George record"
                            fullScreenHandler={setFullScreen}
                            detailsElement={<RecordDetails />}
                        />
                    )}
                </>
            ) : (
                <div className="lloydgeorge_record-stage_fs">
                    <PdfViewer fileUrl={lloydGeorgeUrl} />
                </div>
            )}
        </div>
    );
}

export default LloydGeorgeViewRecordStage;
