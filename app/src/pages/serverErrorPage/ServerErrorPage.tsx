import { useNavigate } from 'react-router';
import { ButtonLink } from 'nhsuk-react-components';
import React from 'react';
import errorCodes from '../../helpers/utils/errorCodes';
import { useSearchParams } from 'react-router-dom';

const ServerErrorPage = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const encodedError = searchParams.get('encodedError') ?? '';
    const [errorCode, interactionId] = JSON.parse(atob(encodedError));

    const defaultMessage = 'An unknown error has occurred.';

    const errorMessage =
        errorCode && !!errorCodes[errorCode] ? errorCodes[errorCode] : defaultMessage;

    return (
        <>
            <h1>Sorry, there is a problem with the service</h1>
            <p>{errorMessage}</p>
            <p>
                Try again by returning to the previous page. You'll need to enter any information
                you submitted again.
            </p>
            <ButtonLink
                onClick={(e) => {
                    e.preventDefault();
                    navigate(-2);
                }}
            >
                Return to previous page
            </ButtonLink>

            <h2>If this error keeps appearing</h2>
            <p>
                <a
                    href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                    target="_blank"
                    rel="noreferrer"
                >
                    Contact the NHS National Service Desk
                </a>{' '}
                or call 0300 303 5678
            </p>

            <p>
                When contacting the service desk, quote this error code as reference:{' '}
                <strong>{interactionId}</strong>
            </p>
        </>
    );
};
export default ServerErrorPage;
