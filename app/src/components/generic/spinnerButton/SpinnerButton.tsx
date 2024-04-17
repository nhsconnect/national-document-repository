import React from 'react';
import { Button } from 'nhsuk-react-components';

export type Props = {
    id: string;
    status: string;
    disabled?: boolean;
};

const SpinnerButton = ({ id, status, disabled }: Props) => {
    return (
        <Button
            id={id}
            aria-label="SpinnerButton"
            className="spinner_button"
            role="SpinnerButton"
            disabled={disabled}
        >
            <output>{status}</output>
        </Button>
    );
};

export default SpinnerButton;
