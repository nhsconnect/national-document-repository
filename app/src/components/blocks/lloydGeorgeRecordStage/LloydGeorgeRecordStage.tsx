import React, { Dispatch, SetStateAction, useState } from 'react';
import {
    BackLink,
    Card,
    Checkboxes,
    Details,
    Fieldset,
    InsetText,
    WarningCallout,
} from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import { Button } from 'nhsuk-react-components';
import PdfViewer from '../../generic/pdfViewer/PdfViewer';
import LloydGeorgeRecordDetails from '../lloydGeorgeRecordDetails/LloydGeorgeRecordDetails';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../helpers/hooks/usePatient';
import LloydGeorgeRecordError from '../lloydGeorgeRecordError/LloydGeorgeRecordError';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import useIsBSOL from '../../../helpers/hooks/useIsBSOL';
import ErrorBox from '../../layout/errorBox/ErrorBox';
import { useForm } from 'react-hook-form';
import { InputRef } from '../../../types/generic/inputRef';

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

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({ reValidateMode: 'onSubmit' });
    const { ref: inputRef, ...checkboxProps } = register('confirmBsol', { required: true });

    const nhsNumber: string = patientDetails?.nhsNumber || '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);

    const role = useRole();
    const isBSOL = useIsBSOL();
    const userIsGpAdminNonBSOL = role === REPOSITORY_ROLE.GP_ADMIN && !isBSOL;

    const PdfCardDescription = () => {
        if (downloadStage === DOWNLOAD_STAGE.PENDING) {
            return <span> Loading...</span>;
        } else if (downloadStage === DOWNLOAD_STAGE.SUCCEEDED) {
            const detailsProps = {
                lastUpdated,
                numberOfFiles,
                totalFileSizeInByte,
                setStage,
                userIsGpAdminNonBSOL: userIsGpAdminNonBSOL,
            };
            return <LloydGeorgeRecordDetails {...detailsProps} />;
        } else {
            return <LloydGeorgeRecordError downloadStage={downloadStage} setStage={setStage} />;
        }
    };

    return (
        <div className="lloydgeorge_record-stage">
            {errors.confirmBsol && (
                <ErrorBox
                    errorBoxSummaryId="78"
                    messageTitle="There is a problem"
                    errorBody="You must confirm if you want to download and remove this record"
                />
            )}
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
            {!fullScreen && userIsGpAdminNonBSOL && (
                <div className="lloydgeorge_record-stage_gp-admin-non-bsol">
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

                        <InsetText>
                            <form
                                onSubmit={handleSubmit(() => {
                                    // Success handler here
                                })}
                                className={
                                    errors.confirmBsol
                                        ? 'nhsuk-form-group--error'
                                        : 'nhsuk-form-group'
                                }
                            >
                                <Fieldset aria-describedby="waste-hint">
                                    <h4>
                                        Are you sure you want to download and remove this record?
                                    </h4>
                                    <Checkboxes
                                        error={
                                            errors.confirmBsol
                                                ? 'Confirm if you want to download and remove this record'
                                                : undefined
                                        }
                                    >
                                        <Checkboxes.Box
                                            inputRef={inputRef as InputRef}
                                            {...checkboxProps}
                                        >
                                            I understand that downloading this record removes it
                                            from storage
                                        </Checkboxes.Box>
                                    </Checkboxes>
                                </Fieldset>

                                <Button type="submit" id="blah">
                                    {' '}
                                    Test submit button{' '}
                                </Button>
                            </form>
                        </InsetText>
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
