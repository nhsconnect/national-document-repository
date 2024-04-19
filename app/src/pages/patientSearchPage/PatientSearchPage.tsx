import React, { useState } from 'react';
import { routes } from '../../types/generic/routes';
import { FieldValues, useForm } from 'react-hook-form';
import ErrorBox from '../../components/layout/errorBox/ErrorBox';
import { Button, Fieldset, Input } from 'nhsuk-react-components';
import SpinnerButton from '../../components/generic/spinnerButton/SpinnerButton';
import { InputRef } from '../../types/generic/inputRef';
import { useNavigate } from 'react-router';
import ServiceError from '../../components/layout/serviceErrorBox/ServiceErrorBox';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import getPatientDetails from '../../helpers/requests/getPatientDetails';
import { SEARCH_STATES } from '../../types/pages/patientSearchPage';
import BackButton from '../../components/generic/backButton/BackButton';
import { AxiosError } from 'axios';
import { PatientDetails } from '../../types/generic/patientDetails';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import { isMock } from '../../helpers/utils/isLocal';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import { errorToParams } from '../../helpers/utils/errorToParams';
import useTitle from '../../helpers/hooks/useTitle';

export const incorrectFormatMessage = "Enter patient's 10 digit NHS number";

function PatientSearchPage() {
    const [, setPatientDetails] = usePatientDetailsContext();
    const [submissionState, setSubmissionState] = useState<SEARCH_STATES>(SEARCH_STATES.IDLE);
    const [statusCode, setStatusCode] = useState<null | number>(null);
    const [inputError, setInputError] = useState<null | string>(null);
    const { register, handleSubmit } = useForm({
        reValidateMode: 'onSubmit',
    });
    const { ref: nhsNumberRef, ...searchProps } = register('nhsNumber', {
        required: incorrectFormatMessage,
        pattern: {
            value: /(^[0-9]{10}$|^[0-9]{3}\s[0-9]{3}\s[0-9]{4}$|^[0-9]{3}-[0-9]{3}-[0-9]{4}$)/,
            message: incorrectFormatMessage,
        },
    });
    const navigate = useNavigate();
    const isError = (statusCode && statusCode >= 500) || !inputError;
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const handleSuccess = (patientDetails: PatientDetails) => {
        setPatientDetails(patientDetails);
        setSubmissionState(SEARCH_STATES.SUCCEEDED);
        navigate(routes.VERIFY_PATIENT);
    };
    const pageTitle = 'Search for patient';
    useTitle({ pageTitle: pageTitle });

    const handleSearch = async (data: FieldValues) => {
        setSubmissionState(SEARCH_STATES.SEARCHING);
        setInputError(null);
        setStatusCode(null);
        const nhsNumber = data.nhsNumber.replace(/[-\s]/gi, '');

        try {
            const patientDetails = await getPatientDetails({
                nhsNumber,
                baseUrl,
                baseHeaders,
            });
            handleSuccess(patientDetails);
        } catch (e) {
            const error = e as AxiosError;
            if (isMock(error)) {
                handleSuccess(buildPatientDetails({ nhsNumber }));
                return;
            }
            if (error.response?.status === 400) {
                setInputError('Enter a valid patient NHS number.');
            } else if (error.response?.status === 403) {
                navigate(routes.SESSION_EXPIRED);
            } else if (error.response?.status === 404) {
                setInputError('Sorry, patient data not found.');
            } else {
                navigate(routes.SERVER_ERROR + errorToParams(error));
            }
            setStatusCode(error.response?.status ?? null);
            setSubmissionState(SEARCH_STATES.FAILED);
        }
    };
    const handleError = (fields: FieldValues) => {
        const errorMessages = Object.entries(fields).map(
            ([k, v]: [string, { message: string }]) => v.message,
        );
        setInputError(errorMessages[0]);
    };
    return (
        <>
            <BackButton />
            {submissionState === SEARCH_STATES.FAILED && (
                <>
                    {isError ? (
                        <ServiceError />
                    ) : (
                        <ErrorBox
                            messageTitle={'There is a problem'}
                            messageLinkBody={inputError}
                            errorInputLink={'#nhs-number-input'}
                            errorBoxSummaryId={'error-box-summary'}
                        />
                    )}
                </>
            )}
            <form onSubmit={handleSubmit(handleSearch, handleError)} noValidate>
                <Fieldset>
                    <Fieldset.Legend headingLevel="h1" isPageHeading>
                        {pageTitle}
                    </Fieldset.Legend>
                    <Input
                        id="nhs-number-input"
                        data-testid="nhs-number-input"
                        label="Enter NHS number"
                        hint="A 10-digit number, for example, 485 777 3456"
                        type="text"
                        {...searchProps}
                        error={
                            submissionState !== SEARCH_STATES.SEARCHING && inputError
                                ? inputError
                                : false
                        }
                        name="nhsNumber"
                        inputRef={nhsNumberRef as InputRef}
                        readOnly={
                            submissionState === SEARCH_STATES.SUCCEEDED ||
                            submissionState === SEARCH_STATES.SEARCHING
                        }
                        autoComplete="off"
                    />
                </Fieldset>
                {submissionState === SEARCH_STATES.SEARCHING ? (
                    <SpinnerButton
                        id="patient-search-spinner"
                        status="Searching..."
                        disabled={true}
                    />
                ) : (
                    <Button type="submit" id="search-submit" data-testid="search-submit-btn">
                        Search
                    </Button>
                )}
            </form>
        </>
    );
}

export default PatientSearchPage;
