import React from 'react';
import useRole from '../../helpers/hooks/useRole';

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
            <strong>What happens with my personal information?</strong>
            <p>NHS England uses this information only to verify your identity.</p>
            <p></p>
            <h2>Feedback form privacy notice</h2>
        </>
    );
}

export default PrivacyPage;
