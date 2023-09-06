import React from 'react';
import type { MouseEvent as ReactEvent } from 'react';
import { ButtonLink } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';

type Props = {};

function HomePage(props: Props) {
    const navigate = useNavigate();

    const navigateUpload = (e: ReactEvent<HTMLAnchorElement, MouseEvent>) => {
        e.preventDefault();
        navigate(routes.SELECT_ORG);
    };

    return (
        <>
            <h1>Inactive Patient Record Administration</h1>
            <p>
                When a patient is inactive, NHS England via Primary Care Support England are
                responsible for administration of their Electronic health record (EHR) and
                attachments until they register at their next GP Practice.
            </p>
            <p>
                General Practice Staff should use this service to upload an inactive patient&apos;s
                electronic health record and attachments.
            </p>
            <p>
                PCSE should use this service to search for and download patient records where there
                has been an access request for an inactive patient health record.
            </p>
            <p>
                If there is an issue with the service please contact the{' '}
                <a
                    href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                    target="_blank"
                    rel="noreferrer"
                >
                    NHS National Service Desk
                </a>
                .
            </p>
            <h2>Before You Start</h2>
            <p>You can only use this service if you have a valid NHS smartcard.</p>
            <ButtonLink role="button" id="start-button" onClick={navigateUpload}>
                Start now
            </ButtonLink>

            {(process.env.REACT_APP_ENVIRONMENT === 'local' ||
                process.env.REACT_APP_ENVIRONMENT === 'development' ||
                process.env.REACT_APP_ENVIRONMENT === 'test') && (
                <div>
                    <br></br>
                    <h2>Test Panel</h2>
                    <p>
                        This section should only be displayed on a test/dev environment and should
                        be used for displaying test configurations
                    </p>
                    <p> API endpoint: {process.env.REACT_APP_DOC_STORE_API_ENDPOINT}</p>
                    <p> Image Version: {process.env.REACT_APP_IMAGE_VERSION}</p>
                </div>
            )}
        </>
    );
}

export default HomePage;
