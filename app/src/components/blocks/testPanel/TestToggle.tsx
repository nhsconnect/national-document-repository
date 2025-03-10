import React from 'react';
import Toggle from 'react-toggle';

export type ToggleProps = {
    id: string;
    checked: boolean;
    label: string;
    onChange: () => void;
};

function TestToggle({ id, checked, onChange, label }: ToggleProps) {
    return (
        <div className="test-toggle-div">
            <Toggle id={id} checked={checked} onChange={onChange} />
            <label htmlFor={id} className="test-toggle-label">
                <p className="test-toggle-paragraph">{label}</p>
            </label>
        </div>
    );
}

export default TestToggle;
