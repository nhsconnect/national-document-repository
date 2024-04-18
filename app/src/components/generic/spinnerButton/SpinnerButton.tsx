import React from 'react';
import { Button } from 'nhsuk-react-components';

export type Props = {
    id: string;
    status: string;
    disabled?: boolean;
};

const SpinnerButton = ({ id, status, disabled }: Props) => {
    return (
        <Button id={id} aria-label={status} className="spinner_button" disabled={disabled}>
            <div className="spinner_button-spinner"></div>
            <output>{status}</output>
        </Button>
    );
};

export default SpinnerButton;
