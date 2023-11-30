import React from 'react';

type Props = {};

function PhaseBanner({}: Props) {
    return (
        <div className="govuk-phase-banner">
            <div className="nhsuk-width-container">
                <p className="govuk-phase-banner__content">
                    <strong className="govuk-tag govuk-phase-banner__content__tag">
                        New Service
                    </strong>
                    <span className="govuk-phase-banner__text">
                        {'This is a new service - your '}
                        <a
                            className="govuk-link"
                            href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                            target="_blank"
                            rel="noreferrer"
                        >
                            feedback
                        </a>
                        {' will help us to improve it.'}
                    </span>
                </p>
            </div>
        </div>
    );
}

export default PhaseBanner;
