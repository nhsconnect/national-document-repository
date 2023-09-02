import React, { useState } from 'react';
import { routes } from '../../types/generic/routes';
import { FieldValues, useForm } from 'react-hook-form';
import ErrorBox from '../../components/layout/errorBox/ErrorBox';
import { Button, Fieldset, Input } from 'nhsuk-react-components';
import SpinnerButton from '../../components/generic/spinnerButton/SpinnerButton';
import { InputRef } from '../../types/generic/inputRef';
import { USER_ROLE } from '../../types/generic/roles';
import { useNavigate } from 'react-router';
import ServiceError from '../../components/layout/serviceErrorBox/ServiceErrorBox';
import { buildPatientDetails } from '../../helpers/test/testBuilders';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';

type Props = {
    role: USER_ROLE;
};

enum SEARCH_STATES {
    IDLE = 'idle',
    SEARCHING = 'searching',
    SUCCEEDED = 'succeeded',
    FAILED = 'failed',
}

function PatientSearchPage({ role }: Props) {
    const [, setPatientDetails] = usePatientDetailsContext();
    const [submissionState, setSubmissionState] = useState<SEARCH_STATES>(SEARCH_STATES.IDLE);
    const [statusCode, setStatusCode] = useState<null | number>(null);
    const [inputError, setInputError] = useState<null | string>(null);
    const { register, handleSubmit } = useForm({
        reValidateMode: 'onSubmit',
    });
    const { ref: nhsNumberRef, ...searchProps } = register('nhsNumber', {
        required: "Enter patient's 10 digit NHS number",
        pattern: {
            value: /(^[0-9]{10}$|^[0-9]{3}\s[0-9]{3}\s[0-9]{4}$|^[0-9]{3}-[0-9]{3}-[0-9]{4}$)/,
            message: "Please enter patient's 10 digit NHS number",
        },
    });
    const navigate = useNavigate();
    const userIsPCSE = role === USER_ROLE.PCSE;
    const userIsGP = role === USER_ROLE.GP;
    const isError = (statusCode && statusCode >= 500) || !inputError;

    const handleSearch = (data: FieldValues) => {
        setInputError(null);
        setStatusCode(null);

        setSubmissionState(SEARCH_STATES.SEARCHING);
        const nhsNumber = data.nhsNumber.replace(/[-\s]/gi, '');

        const patientDetails = buildPatientDetails({ nhsNumber });
        setPatientDetails(patientDetails);

        setSubmissionState(SEARCH_STATES.SUCCEEDED);
        // GP Role
        if (userIsGP) {
            // Make PDS patient search request to upload documents to patient
            navigate(routes.UPLOAD_VERIFY);
        }

        // PCSE Role
        else if (userIsPCSE) {
            // Make PDS and Dynamo document store search request to download documents from patient
            navigate(routes.DOWNLOAD_VERIFY);
        }
    };

    const handleError = async () => {
        setSubmissionState(SEARCH_STATES.FAILED);
        setInputError("Enter patient's 10 digit NHS number");
    };

    return (
        <>
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
                        Search for patient
                    </Fieldset.Legend>
                    <Input
                        id="nhs-number-input"
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
                    />
                </Fieldset>
                {submissionState === SEARCH_STATES.SEARCHING ? (
                    <SpinnerButton status="Searching..." disabled={true} />
                ) : (
                    <Button type="submit">Search</Button>
                )}
            </form>
        </>
    );
}

export default PatientSearchPage;
