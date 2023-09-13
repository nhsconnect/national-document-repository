import { BackLink } from 'nhsuk-react-components';
import React from 'react';
import type { MouseEvent } from 'react';
import { useNavigate } from 'react-router';

const BackButton = () => {
    const navigate = useNavigate();

    const onBack = (e: MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        navigate(-1);
    };

    return (
        <BackLink className="clickable" onClick={onBack}>
            Back
        </BackLink>
    );
};

export default BackButton;
