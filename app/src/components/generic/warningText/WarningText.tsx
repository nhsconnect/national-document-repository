import React, { ReactNode } from 'react';
import { Button } from 'nhsuk-react-components';

export type Props = { children: ReactNode };

const WarningText = ({ children }: Props) => {
    return (
        <div className="govuk-warning-text">
            <span className="govuk-warning-text__icon" aria-hidden="true">
                !
            </span>
            <strong className="govuk-warning-text__text">
                <span className="nhsuk-u-visually-hidden">Warning</span>
                {children}
            </strong>
        </div>
    );
};

export default WarningText;
