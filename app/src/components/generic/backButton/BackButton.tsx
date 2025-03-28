import { BackLink } from 'nhsuk-react-components';
import React from 'react';
import type { MouseEvent } from 'react';
import { useNavigate } from 'react-router-dom';

interface BackButtonProps {
    toLocation?: string;
    backLinkText?: string;
    dataTestid?: string;
}

const BackButton = ({ toLocation, dataTestid, backLinkText = 'Go back' }: BackButtonProps) => {
    const navigate = useNavigate();

    const onBack = (e: MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();

        if (toLocation) navigate(toLocation);
        else navigate(-1);
    };

    return (
        <BackLink onClick={onBack} href="#" data-testid={dataTestid}>
            {backLinkText}
        </BackLink>
    );
};

export default BackButton;
