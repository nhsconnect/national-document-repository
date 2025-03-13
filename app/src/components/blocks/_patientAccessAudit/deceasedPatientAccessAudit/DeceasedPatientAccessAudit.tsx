import { Button, Checkboxes, Textarea } from 'nhsuk-react-components';
import usePatient from '../../../../helpers/hooks/usePatient';
import useTitle from '../../../../helpers/hooks/useTitle';
import { FieldValues, SubmitHandler, useForm } from 'react-hook-form';
import { useState } from 'react';
import { routes } from '../../../../types/generic/routes';
import { Link, useNavigate } from 'react-router-dom';
import BackButton from '../../../generic/backButton/BackButton';
import {
    AccessAuditData,
    AccessAuditType,
    DeceasedAccessAuditReasons,
    PatientAccessAudit,
} from '../../../../types/generic/accessAudit';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import { AxiosError } from 'axios';
import { isMock } from '../../../../helpers/utils/isLocal';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import { InputRef } from '../../../../types/generic/inputRef';
import { TextAreaRef } from '../../../../types/generic/textareaRef';
import { usePatientAccessAuditContext } from '../../../../providers/patientAccessAuditProvider/PatientAccessAuditProvider';
import SpinnerButton from '../../../generic/spinnerButton/SpinnerButton';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';
import postPatientAccessAudit from '../../../../helpers/requests/postPatientAccessAudit';

type Props = {};

enum FORM_FIELDS {
    Reasons = 'reasons',
    OtherReasonText = 'otherReasonText',
}
type FormData = {
    [FORM_FIELDS.Reasons]: string[];
    [FORM_FIELDS.OtherReasonText]: string;
};

const DeceasedPatientAccessAudit = (props: Props) => {
    /* HOOKS */
    const pageTitle = 'Deceased patient record';
    useTitle({ pageTitle });

    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();

    const navigate = useNavigate();

    const [patientAccessAudit, setPatientAccessAudit] = usePatientAccessAuditContext();

    const patientDetails = usePatient();
    const deceasedPatientAccessAudit = patientAccessAudit?.find(
        (audit) =>
            audit.accessAuditType === AccessAuditType.deceasedPatient &&
            audit.nhsNumber === patientDetails?.nhsNumber,
    );

    const {
        register,
        handleSubmit,
        getValues,
        formState: { errors },
    } = useForm<FormData>({
        reValidateMode: 'onSubmit',
        shouldFocusError: true,
        defaultValues: {
            reasons: deceasedPatientAccessAudit?.accessAuditData.Reasons ?? [],
            otherReasonText: deceasedPatientAccessAudit?.accessAuditData.OtherReasonText ?? '',
        },
    });

    const [inputError, setInputError] = useState<undefined | string>(undefined);
    const [anotherReasonSelected, setAnotherReasonSelected] = useState<boolean>(
        deceasedPatientAccessAudit?.accessAuditData.Reasons.includes(
            DeceasedAccessAuditReasons.anotherReason,
        ) ?? false,
    );
    const [submitting, setSubmitting] = useState<boolean>(false);
    /* HOOKS */

    if (!patientDetails) {
        navigate(routes.SEARCH_PATIENT);
        return <></>;
    }

    const { ref: checkboxInputRef, ...checkboxProps } = register(FORM_FIELDS.Reasons, {
        required: 'Select a reason why you need to access this record',
        validate: () => {
            const selectedReasons = getValues()[FORM_FIELDS.Reasons];

            if (selectedReasons.length === 0) {
                return false;
            }

            setAnotherReasonSelected(
                selectedReasons.includes(DeceasedAccessAuditReasons.anotherReason),
            );

            return true;
        },
        onChange: () => {
            const selectedReasons = getValues()[FORM_FIELDS.Reasons] ?? [];
            setAnotherReasonSelected(
                selectedReasons.includes(DeceasedAccessAuditReasons.anotherReason),
            );
        },
    });

    const { ref: textareaInputRef, ...textareaProps } = register(FORM_FIELDS.OtherReasonText, {
        validate: (value) => {
            if (!anotherReasonSelected || value?.length > 0) {
                return true;
            }

            return 'Enter a reason why you need to access this record';
        },
    });

    const submitForm: SubmitHandler<FormData> = async (formData) => {
        const accessAuditData: AccessAuditData = {
            Reasons: formData.reasons,
            OtherReasonText: formData.reasons.includes(DeceasedAccessAuditReasons.anotherReason)
                ? formData.otherReasonText
                : '',
        };

        try {
            setSubmitting(true);

            await postPatientAccessAudit({
                accessAuditData,
                accessAuditType: AccessAuditType.deceasedPatient,
                baseUrl,
                baseHeaders,
                nhsNumber: patientDetails!.nhsNumber,
            });

            setSubmitting(false);

            handleSuccess(accessAuditData);
        } catch (e) {
            const error = e as AxiosError;

            if (isMock(error)) {
                handleSuccess(accessAuditData);
            } else if (error.code === '403') {
                navigate(routes.SESSION_EXPIRED);
            } else {
                navigate(routes.SERVER_ERROR + errorToParams(error));
            }
        }
    };

    const handleSuccess = (accessAuditData: AccessAuditData) => {
        const newPatientAccessAudit = patientAccessAudit?.map((audit): PatientAccessAudit => {
            if (
                audit.accessAuditType === AccessAuditType.deceasedPatient &&
                audit.nhsNumber === patientDetails?.nhsNumber
            ) {
                return {
                    ...audit,
                    accessAuditData,
                    nhsNumber: patientDetails?.nhsNumber,
                } as PatientAccessAudit;
            }

            return audit;
        }) ?? [
            {
                accessAuditType: AccessAuditType.deceasedPatient,
                accessAuditData,
                nhsNumber: patientDetails?.nhsNumber,
            } as PatientAccessAudit,
        ];

        setPatientAccessAudit(newPatientAccessAudit);
        navigate(routes.LLOYD_GEORGE);
    };

    const handleError = (fields: FieldValues) => {
        const errorMessages = Object.entries(fields).map(
            ([k, v]: [string, { message: string }]) => v.message,
        );
        setInputError(errorMessages[0]);
    };

    const ReasonCheckbox = (reason: DeceasedAccessAuditReasons, label: string) => {
        const key = `reason-checkbox-${reason}`;

        return (
            <Checkboxes.Box
                key={key}
                data-testid={key}
                value={reason}
                inputRef={checkboxInputRef as InputRef}
                {...checkboxProps}
            >
                {label}
            </Checkboxes.Box>
        );
    };

    return (
        <div className="deceased-patient-access-page">
            <BackButton toLocation={routes.SEARCH_PATIENT} />

            {inputError && (
                <ErrorBox
                    dataTestId="access-reason-error-box"
                    errorBoxSummaryId="access-reason"
                    messageTitle="There is a problem"
                    errorBody={inputError}
                />
            )}

            <h1 data-testid="title">{pageTitle}</h1>
            <div className="patient-details">
                <label>
                    <strong>
                        {patientDetails!.familyName}, {patientDetails!.givenName}
                    </strong>
                </label>
                <label data-testid="nhs-number">
                    NHS number: {formatNhsNumber(patientDetails!.nhsNumber)}
                </label>
                <label>
                    Date of birth: {getFormattedDate(new Date(patientDetails!.birthDate))}
                </label>
            </div>

            <h2>Why do you need to access this record</h2>
            <form onSubmit={handleSubmit(submitForm, handleError)}>
                <Checkboxes name="access-reason" id="access-reason" error={errors.reasons?.message}>
                    {ReasonCheckbox(
                        DeceasedAccessAuditReasons.medicalRequest,
                        "to respond to a Coroner's or Medical Examiner's request",
                    )}
                    {ReasonCheckbox(
                        DeceasedAccessAuditReasons.legalRequest,
                        'to respond to a legal or insurance request',
                    )}
                    {ReasonCheckbox(
                        DeceasedAccessAuditReasons.familyRequest,
                        'to respond to a request from a family member or personal representative of the patient',
                    )}
                    {ReasonCheckbox(
                        DeceasedAccessAuditReasons.internalNhsRequest,
                        'to respond to an internal NHS request',
                    )}
                    {ReasonCheckbox(
                        DeceasedAccessAuditReasons.removeRecord,
                        'to remove this record at the end of its retention period',
                    )}
                    <Checkboxes.Divider />
                    {ReasonCheckbox(DeceasedAccessAuditReasons.anotherReason, 'another reason')}
                    {anotherReasonSelected && (
                        <Textarea
                            data-testid={FORM_FIELDS.OtherReasonText}
                            rows={4}
                            error={errors.otherReasonText?.message}
                            textareaRef={textareaInputRef as TextAreaRef}
                            {...textareaProps}
                        />
                    )}
                </Checkboxes>
                <div className="button-container">
                    {submitting ? (
                        <SpinnerButton
                            id="submitting-spinner"
                            status="Loading record"
                            disabled={true}
                        />
                    ) : (
                        <>
                            <Button type="submit" id="form-submit" data-testid="form-submit-button">
                                Continue to the record
                            </Button>
                            <Link
                                className="ml-6"
                                to={routes.SEARCH_PATIENT}
                                data-testid="back-to-search-button"
                            >
                                Go back to Search for a patient
                            </Link>
                        </>
                    )}
                </div>
            </form>
        </div>
    );
};

export default DeceasedPatientAccessAudit;
