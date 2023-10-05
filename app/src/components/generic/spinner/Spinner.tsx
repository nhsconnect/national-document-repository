import React from 'react';

type Props = {
    status: string;
};

const Spinner = ({ status }: Props) => {
    return (
        <div className="nhsuk-loader" aria-label={status}>
            <span className="nhsuk-loader__text" role="status">
                {status}
            </span>
            <span className="spinner-blue"></span>
        </div>
    );
};

export default Spinner;
