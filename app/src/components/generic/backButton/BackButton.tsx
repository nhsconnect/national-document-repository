import { BackLink } from 'nhsuk-react-components';
import React from 'react';
import type { MouseEvent } from 'react';
import { useNavigate, useLocation } from 'react-router';
import { endpoints } from '../../../types/generic/endpoints';
import { routes } from '../../../types/generic/routes';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';

const BackButton = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const baseAPIUrl = useBaseAPIUrl();

    const onBack = (e: MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        if (
            location.pathname === routes.UPLOAD_SEARCH ||
            location.pathname === routes.DOWNLOAD_SEARCH
        ) {
            window.location.replace(`${baseAPIUrl}${endpoints.LOGIN}`);
        } else {
            navigate(-1);
        }
    };

    return (
        <BackLink className="clickable" onClick={onBack}>
            Back
        </BackLink>
    );
};

export default BackButton;
