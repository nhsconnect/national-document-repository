import React from 'react';
import { Button } from 'nhsuk-react-components';

export type Props = {
    status: string;
    disabled?: boolean;
};

const SpinnerButton = ({ status, disabled }: Props) => {
    return (
        <Button
            aria-label="SpinnerButton"
            className="spinner_button"
            role="SpinnerButton"
            disabled={disabled}
        >
            <div className="spinner_button-spinner"></div>
            <div role="status">{status}</div>
        </Button>
    );
};

export default SpinnerButton;
