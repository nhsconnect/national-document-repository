import React from 'react';

function PhaseBanner() {
    return (
        <div className="govuk-phase-banner">
            <div className="nhsuk-width-container">
                <p className="govuk-phase-banner__content">
                    <strong className="govuk-tag govuk-phase-banner__content__tag">
                        New Service
                    </strong>
                    <span className="govuk-phase-banner__text">
                        Your feedback will help us to improve this service.
                    </span>
                </p>
            </div>
        </div>
    );
}

export default PhaseBanner;
