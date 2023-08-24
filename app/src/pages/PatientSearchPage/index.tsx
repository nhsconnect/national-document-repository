import React, { useState } from 'react';
import { routes } from '../../types/blocks/routes';
import { useForm } from 'react-hook-form';
import ErrorBox from '../../components/layout/ErrorBox';

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
    // GP Role
    if (userIsGP) {
      // Make PDS patient search request
    }

    // PCSE Role
    else if (userIsPCSE) {
      // Make PDS and Dynamo document store search request
    }
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
    </>
  );
}

export default PatientSearchPage;
