import React from 'react';

type Props = {
    status: string;
};

const Spinner = ({ status }: Props) => {
    return (
        <div className="nhsuk-loader" aria-label={status}>
            <output className="nhsuk-loader__text">{status}</output>
            <span className="spinner-blue"></span>
        </div>
    );
};

export default Spinner;
