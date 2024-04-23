import React from 'react';

export type Props = { text: string; iconFallbackText?: string };

const WarningText = ({ text, iconFallbackText = 'warning' }: Props) => {
    return (
        <div className="govuk-warning-text">
            <span className="govuk-warning-text__icon" aria-hidden="true">
                !
            </span>
            <strong className="govuk-warning-text__text">
                <span className="nhsuk-u-visually-hidden">{iconFallbackText}</span>
                <p>{text}</p>
            </strong>
        </div>
    );
};

export default WarningText;
