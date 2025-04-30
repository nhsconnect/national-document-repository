import React from 'react';
import { routes } from '../../../types/generic/routes';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';
import { Link } from 'react-router-dom';
import { Tag } from 'nhsuk-react-components';

function PhaseBanner() {
    const [session] = useSessionContext();
    const { isLoggedIn } = session;
    const linkToFeedbackPage = isLoggedIn ? (
        <Link
            to={routes.FEEDBACK}
            target="_blank"
            rel="opener"
            aria-label="feedback - this link will open in a new tab"
        >
            feedback
        </Link>
    ) : (
        'feedback'
    );

    return (
        <div className="govuk-phase-banner">
            <div className="nhsuk-width-container">
                <div className="govuk-phase-banner__content">
                    <Tag className="govuk-phase-banner__content__tag ">New service</Tag>
                    <p className="govuk-phase-banner__text">
                        Your {linkToFeedbackPage} will help us to improve this service.
                    </p>
                </div>
            </div>
        </div>
    );
}

export default PhaseBanner;
