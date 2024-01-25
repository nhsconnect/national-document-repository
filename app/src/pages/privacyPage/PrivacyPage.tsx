import React from 'react';
import useRole from '../../helpers/hooks/useRole';
import { routes } from '../../types/generic/routes';
import { Link } from 'react-router-dom';

type Props = {};

function PrivacyPage() {
    const isLoggedIn = !!useRole();
    return (
        <>
            <h1>Privacy notice</h1>
            <p>
                If you access the Lloyd George patient records digital service using your{' '}
                <a
                    target="_blank"
                    href="https://am.nhsidentity.spineservices.nhs.uk/openam/XUI/?realm=/#/"
                    rel="noreferrer"
                >
                    NHS Care Identity
                </a>{' '}
                credentials, your NHS Care Identity credentials are managed by NHS England.
            </p>
            <p>
                This means NHS England is the data controller for any personal information that you
                provided to get NHS Care Identity credentials.
            </p>
            <h4>What happens with my personal information?</h4>
            <p>NHS England uses this information only to verify your identity.</p>
            <p>
                When verifying your identity, our role is a “processor”. We must act under
                instructions provided by NHS England (the “controller”).
            </p>
            <p>
                To find out more about NHS England's Privacy Notice and its Terms and Conditions,
                view the{' '}
                <a
                    target="_blank"
                    href="https://digital.nhs.uk/services/care-identity-service"
                    rel="noreferrer"
                >
                    NHS Care Identity Service
                </a>{' '}
                .
            </p>
            <p>This only applies to information you provide through NHS England.</p>
            <h2>Feedback form privacy notice</h2>
            <p>
                When submitting your details using our{' '}
                {isLoggedIn ? <Link to={routes.FEEDBACK}></Link> : <span>feedback form</span>}, any
                personal information you give to us will be processed in accordance with the{' '}
                <a
                    target="_blank"
                    href="https://digital.nhs.uk/data-and-information/keeping-data-safe-and-benefitting-the-public/gdpr#:~:text=The%20GDPR%20came%20into%20effect,in%20line%20with%20the%20regulations."
                    rel="noreferrer"
                >
                    UK General Data Protection Regulation (GDPR) 2018
                </a>{' '}
                .
            </p>
            <p>
                We use the information you submitted to process your request and provide relevant
                information or services you have requested.
            </p>
            <p>This will help support us in developing this service.</p>
        </>
    );
}

export default PrivacyPage;
