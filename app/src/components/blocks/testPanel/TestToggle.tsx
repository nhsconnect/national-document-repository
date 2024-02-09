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
        <div
            style={{
                display: 'flex',
                flexFlow: 'row nowrap',
                alignItems: 'center',
                marginBottom: '12px',
            }}
        >
            <Toggle id={id} checked={checked} onChange={onChange} />
            <label htmlFor={id} style={{ marginLeft: '6px' }}>
                <p style={{ marginBottom: '0px' }}>{label}</p>
            </label>
        </div>
    );
}

export default TestToggle;
