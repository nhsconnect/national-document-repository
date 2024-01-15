import React from 'react';
import { routes } from '../../../types/generic/routes';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';

function PhaseBanner() {
    const [session] = useSessionContext();
    const { isLoggedIn } = session;
    const linkToFeedbackPage = isLoggedIn ? (
        <>
            <a href={routes.FEEDBACK} target="_blank" rel="noreferrer">
                feedback
            </a>
        </>
    ) : (
        'feedback'
    );

    return (
        <div className="govuk-phase-banner">
            <div className="nhsuk-width-container">
                <p className="govuk-phase-banner__content">
                    <strong className="govuk-tag govuk-phase-banner__content__tag">
                        New Service
                    </strong>
                    <span className="govuk-phase-banner__text">
                        Your {linkToFeedbackPage} will help us to improve this service.
                    </span>
                </p>
            </div>
        </div>
    );
}

export default PhaseBanner;
