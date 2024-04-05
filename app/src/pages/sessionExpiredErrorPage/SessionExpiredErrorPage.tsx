import { useNavigate } from 'react-router';
import { ButtonLink } from 'nhsuk-react-components';
import React from 'react';
import { unixTimestamp } from '../../helpers/utils/createTimestamp';
import { routes } from '../../types/generic/routes';

const SessionExpiredErrorPage = () => {
    const navigate = useNavigate();

    return (
        <>
            <h1>You have been logged out</h1>
            <p>
                Your session has automatically expired following a period of inactivity. This is to
                protect patient security.
            </p>
            <p>Log in again to use this service.</p>
            <ButtonLink
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    navigate(routes.START);
                }}
            >
                Return to start and log in again
            </ButtonLink>

            <h2>If this error keeps appearing</h2>
            <p>
                <a
                    href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                    target="_blank"
                    rel="noreferrer"
                >
                    Contact the NHS National Service Desk (opens in a new tab)
                </a>{' '}
                or call 0300 303 5678
            </p>

            <p>
                When contacting the service desk, quote this error code as reference:{' '}
                <strong>{unixTimestamp()}</strong>
            </p>
        </>
    );
};
export default SessionExpiredErrorPage;
