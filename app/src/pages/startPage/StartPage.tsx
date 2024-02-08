import React, { useState } from 'react';
import type { MouseEvent } from 'react';
import { ButtonLink } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import Spinner from '../../components/generic/spinner/Spinner';
import { routes } from '../../types/generic/routes';
import { endpoints } from '../../types/generic/endpoints';
import { isLocal } from '../../helpers/utils/isLocal';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import TestPanel from '../../components/blocks/testPanel/TestPanel';

type Props = {};

function StartPage(props: Props) {
    const navigate = useNavigate();
    const baseAPIUrl = useBaseAPIUrl();
    const [isLoading, setIsLoading] = useState(false);
    const handleLogin = (e: MouseEvent<HTMLAnchorElement>) => {
        setIsLoading(true);
        e.preventDefault();
        if (isLocal) {
            navigate(routes.AUTH_CALLBACK);
        } else {
            window.location.replace(`${baseAPIUrl}${endpoints.LOGIN}`);
        }
    };

    return !isLoading ? (
        <>
            <h1>Access and store digital GP records</h1>
            <p>
                This service gives you access to Lloyd George digital health records. You may have
                received a note within a patient record, stating that the record has been digitised.
            </p>
            <p>If you are part of a GP practice, you can use this service to:</p>
            <ul>
                <li>view a patient record</li>
                <li>download a patient record</li>
                <li>remove a patient record</li>
            </ul>
            <p>If you are managing records on behalf of NHS England, you can:</p>
            <ul>
                <li>download a patient record</li>
            </ul>
            <p>Not every patient will have a digital record available.</p>
            <h2>Before you start</h2>
            <p>You’ll be asked for:</p>
            <ul>
                <li>your NHS smartcard</li>
                <li>patient details including their name, date of birth and NHS number</li>
            </ul>
            <ButtonLink role="button" data-testid="start-btn" onClick={handleLogin}>
                Start now
            </ButtonLink>
            <h3>Get support with the service</h3>
            {'Contact the '}
            <a
                href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                target="_blank"
                rel="noreferrer"
            >
                NHS National Service Desk
            </a>
            {' if there is an issue with this service or call 0300 303 5678.'}
            {process.env.REACT_APP_ENVIRONMENT === 'local' ||
                process.env.REACT_APP_ENVIRONMENT === 'development' ||
                (process.env.REACT_APP_ENVIRONMENT === 'test' && <TestPanel />)}
        </>
    ) : (
        <Spinner status="Logging in..." />
    );
}

export default StartPage;
