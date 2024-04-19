import React, { Dispatch, SetStateAction, useState } from 'react';
import {
    BackLink,
    Button,
    Card,
    Checkboxes,
    Details,
    Fieldset,
    InsetText,
    WarningCallout,
} from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../../generic/pdfViewer/PdfViewer';
import LloydGeorgeRecordDetails from '../lloydGeorgeRecordDetails/LloydGeorgeRecordDetails';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../helpers/hooks/usePatient';
import LloydGeorgeRecordError from '../lloydGeorgeRecordError/LloydGeorgeRecordError';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import useIsBSOL from '../../../helpers/hooks/useIsBSOL';
import WarningText from '../../generic/warningText/WarningText';
import ErrorBox from '../../layout/errorBox/ErrorBox';
import { useForm } from 'react-hook-form';
import { InputRef } from '../../../types/generic/inputRef';
import BackButton from '../../generic/backButton/BackButton';
import { actionLinks } from '../../../types/blocks/lloydGeorgeActions';
import { Link, useNavigate } from 'react-router-dom';

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
}: Props) {
    const [fullScreen, setFullScreen] = useState(false);
    const [downloadRemoveButtonClicked, setDownloadRemoveButtonClicked] = useState(false);
    const patientDetails = usePatient();
    const dob: string = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';
    const navigate = useNavigate();
    const { register, handleSubmit, formState, clearErrors, setError, setFocus } = useForm({
        reValidateMode: 'onSubmit',
    });
    const { ref: inputRef, ...checkboxProps } = register('confirmDownloadRemove', {
        required: true,
    });
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const role = useRole();
    const isBSOL = useIsBSOL();
    const userIsGpAdminNonBSOL = role === REPOSITORY_ROLE.GP_ADMIN && !isBSOL;
    const hasMenuAccess = actionLinks.some((l) => role && !l.unauthorised?.includes(role));

    const PdfCardDescription = () => {
        if (downloadStage === DOWNLOAD_STAGE.PENDING) {
            return <span> Loading...</span>;
        } else if (downloadStage === DOWNLOAD_STAGE.SUCCEEDED) {
            const detailsProps = {
                lastUpdated,
                numberOfFiles,
                totalFileSizeInByte,
                setStage,
                setDownloadRemoveButtonClicked,
                downloadRemoveButtonClicked,
                setError,
                setFocus,
            };
            return <LloydGeorgeRecordDetails {...detailsProps} />;
        } else {
            return <LloydGeorgeRecordError downloadStage={downloadStage} setStage={setStage} />;
        }
    };

    const handleConfirmDownloadAndRemoveButton = () => {
        setStage(LG_RECORD_STAGE.DOWNLOAD_ALL);
    };

    const handleCancelButton = () => {
        setDownloadRemoveButtonClicked(false);
        clearErrors('confirmDownloadRemove');
    };

    const PdfCard = () => (
        <Card className="lloydgeorge_record-stage_pdf">
            <Card.Content data-testid="pdf-card" className="lloydgeorge_record-stage_pdf-content">
                <Card.Heading
                    className="lloydgeorge_record-stage_pdf-content-label"
                    headingLevel="h1"
                >
                    Lloyd George record
                </Card.Heading>
                <PdfCardDescription />
            </Card.Content>
            {downloadStage === DOWNLOAD_STAGE.SUCCEEDED && (
                <Details expander open className="lloydgeorge_record-stage_pdf-expander">
                    <Details.Summary
                        style={{ display: 'inline-block' }}
                        data-testid="view-record-bin"
                    >
                        View record
                    </Details.Summary>
                    <button
                        className="lloydgeorge_record-stage_pdf-expander-button link-button clickable"
                        data-testid="full-screen-btn"
                        onClick={() => {
                            setFullScreen(true);
                        }}
                    >
                        View in full screen
                    </button>
                    <PdfViewer fileUrl={lloydGeorgeUrl} />
                </Details>
            )}
        </Card>
    );

    const updateActions = actionLinks.filter(
        (l) => !!l.href && role && !l.unauthorised?.includes(role),
    );
    const downloadActions = actionLinks.filter(
        (l) => !!l.stage && role && !l.unauthorised?.includes(role),
    );

    const MenuCard = () => (
        <Card className="lloydgeorge_record-stage_menu">
            <Card.Content className="lloydgeorge_record-stage_menu-content">
                {!!updateActions.length && (
                    <>
                        <h4>Update record</h4>
                        <ol>
                            {updateActions.map((link) => (
                                <li key={link.key} data-testid={link.key}>
                                    <Link
                                        to="#placeholder"
                                        onClick={(e) => {
                                            e.preventDefault();
                                            if (link.href) navigate(link.href);
                                        }}
                                    >
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ol>
                    </>
                )}
                {!!downloadActions.length && (
                    <>
                        <h4>Download record</h4>
                        <ol>
                            {downloadActions.map((link) => (
                                <li key={link.key} data-testid={link.key}>
                                    <Link
                                        to="#placeholder"
                                        onClick={(e) => {
                                            e.preventDefault();
                                            if (link.href) navigate(link.href);
                                        }}
                                    >
                                        {link.label}
                                    </Link>
                                </li>
                            ))}
                        </ol>
                    </>
                )}
            </Card.Content>
        </Card>
    );

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
                    onClick={() => {
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
                    {hasMenuAccess ? (
                        <div className="lloydgeorge_record-stage_flex">
                            <div className="lloydgeorge_record-stage_flex-row">
                                <MenuCard />
                            </div>
                            <div className="lloydgeorge_record-stage_flex-row">
                                <PdfCard />
                            </div>
                        </div>
                    ) : (
                        <PdfCard />
                    )}
                </>
            ) : (
                <PdfViewer fileUrl={lloydGeorgeUrl} />
            )}
        </div>
    );
}

export default LloydGeorgeRecordStage;
