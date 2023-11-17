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
        if (location.pathname === '/search/upload' || location.pathname === '/search/patient') {
            window.location.replace(`${baseAPIUrl}${endpoints.LOGIN}`);
        } else {
            navigate(-1);
        }
    };

    // const onSearchPage = () => {
    //     (location.pathname.includes('/search/upload') ||
    //         location.pathname.includes('/search/patient')) &&
    //         !(
    //             location.pathname.includes('/result') ||
    //             location.pathname.includes('/results') ||
    //             location.pathname.includes('/delete') ||
    //             location.pathname.includes('/upload') ||
    //             location.pathname.includes('/submit') ||
    //             location.pathname.includes('/lloyd-george-record')
    //         );
    // };

    return (
        <BackLink className="clickable" onClick={onBack}>
            Back
        </BackLink>
    );
};

export default BackButton;
