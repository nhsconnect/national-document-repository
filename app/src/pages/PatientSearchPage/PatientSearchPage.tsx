import React, { useState } from 'react';
import { routes } from '../../types/generic/routes';
import { useForm } from 'react-hook-form';
import ErrorBox from '../../components/layout/errorBox/ErrorBox';
import ServiceError from '../serviceError/ServiceError';
import { Button, Fieldset, Input } from 'nhsuk-react-components';
import SpinnerButton from '../../components/generic/spinnerButton/SpinnerButton';
import { InputRef } from '../../types/generic/inputRef';

type Props = {
  route: routes;
};

enum SEARCH_STATES {
  IDLE = 'idle',
  SEARCHING = 'searching',
  SUCCEEDED = 'succeeded',
  FAILED = 'failed'
}

function PatientSearchPage({ route }: Props) {
  const [submissionState, setSubmissionState] = useState<SEARCH_STATES>(
    SEARCH_STATES.IDLE
  );
  const [statusCode, setStatusCode] = useState<null | number>(null);
  const [inputError, setInputError] = useState<null | string>(null);
  const { register, handleSubmit } = useForm({
    reValidateMode: 'onSubmit'
  });
  const { ref: nhsNumberRef, ...searchProps } = register('nhsNumber', {
    required: "Enter patient's 10 digit NHS number",
    pattern: {
      value:
        /(^[0-9]{10}$|^[0-9]{3}\s[0-9]{3}\s[0-9]{4}$|^[0-9]{3}-[0-9]{3}-[0-9]{4}$)/,
      message: "Enter patient's 10 digit NHS number"
    }
  });

  const userIsPCSE = route === routes.DOWNLOAD_SEARCH;
  const userIsGP = route === routes.UPLOAD_SEARCH;
  const isError = (statusCode && statusCode >= 500) || !inputError;

  const handleSearch = () => {
    setSubmissionState(SEARCH_STATES.SEARCHING);
    // GP Role
    if (userIsGP) {
      // Make PDS patient search request
    }

    // PCSE Role
    else if (userIsPCSE) {
      // Make PDS and Dynamo document store search request
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
          <Fieldset.Legend headingLevel='h1' isPageHeading>
            Search for patient
          </Fieldset.Legend>
          <Input
            id='nhs-number-input'
            label='Enter NHS number'
            hint='A 10-digit number, for example, 485 777 3456'
            type='text'
            {...searchProps}
            error={
              submissionState !== SEARCH_STATES.SEARCHING && inputError
                ? inputError
                : false
            }
            name='nhsNumber'
            inputRef={nhsNumberRef as InputRef}
            readOnly={
              submissionState === SEARCH_STATES.SUCCEEDED ||
              submissionState === SEARCH_STATES.SEARCHING
            }
          />
        </Fieldset>
        {submissionState === SEARCH_STATES.SEARCHING ? (
          <SpinnerButton status='Searching...' disabled={true} />
        ) : (
          <Button type='submit'>Search</Button>
        )}
      </form>
    </>
  );
}

export default PatientSearchPage;
