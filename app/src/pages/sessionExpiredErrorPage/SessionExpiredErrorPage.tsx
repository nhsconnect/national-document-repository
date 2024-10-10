import { ButtonLink } from 'nhsuk-react-components';
import React, { MouseEvent, useState } from 'react';
import { endpoints } from '../../types/generic/endpoints';
import Spinner from '../../components/generic/spinner/Spinner';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import useTitle from '../../helpers/hooks/useTitle';
import { isLocal } from '../../helpers/utils/isLocal';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';

const SessionExpiredErrorPage = () => {
    const baseAPIUrl = useBaseAPIUrl();
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const handleLogin = (e: MouseEvent<HTMLAnchorElement>) => {
        setIsLoading(true);
        e.preventDefault();
        if (isLocal) {
            navigate(routes.AUTH_CALLBACK);
        } else {
            window.location.replace(`${baseAPIUrl}${endpoints.LOGIN}`);
        }
    };
    const pageHeader = 'We signed you out due to inactivity';
    useTitle({ pageTitle: pageHeader });
    return !isLoading ? (
        <>
            <h1>{pageHeader}</h1>
            <p>
                This is to protect your information. You'll need to enter any information you
                submitted again.
            </p>
            <ButtonLink href="#" onClick={handleLogin}>
                Sign back in
            </ButtonLink>
        </>
    ) : (
        <Spinner status="Signing in..." />
    );
};
export default SessionExpiredErrorPage;
