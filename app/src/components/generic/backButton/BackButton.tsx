import { BackLink } from 'nhsuk-react-components';
import React from 'react';
import type { MouseEvent } from 'react';
import { useNavigate, useLocation } from 'react-router';
import { endpoints } from '../../../types/generic/endpoints';
import { useBaseAPIUrl } from '../../../providers/configProvider/ConfigProvider';

const BackButton = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const baseAPIUrl = useBaseAPIUrl();

    const onBack = (e: MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        if (
            location.pathname.includes('/search/upload') ||
            location.pathname.includes('/search/patient')
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
