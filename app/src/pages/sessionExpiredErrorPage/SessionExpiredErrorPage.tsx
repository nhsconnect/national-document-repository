import { ButtonLink } from 'nhsuk-react-components';
import React, { MouseEvent, useState } from 'react';
import { endpoints } from '../../types/generic/endpoints';
import Spinner from '../../components/generic/spinner/Spinner';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';

const SessionExpiredErrorPage = () => {
    const baseAPIUrl = useBaseAPIUrl();
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = (e: MouseEvent<HTMLAnchorElement>) => {
        setIsLoading(true);
        e.preventDefault();
        window.location.replace(`${baseAPIUrl}${endpoints.LOGIN}`);
    };

    return !isLoading ? (
        <>
            <h1>We signed you out due to inactivity</h1>
            <p>
                This is to protect your information. You'll need to enter any information you
                submitted again.
            </p>
            <ButtonLink href="#" onClick={handleLogin}>
                Sign back in
            </ButtonLink>
        </>
    ) : (
        <Spinner status="Logging in..." />
    );
};
export default SessionExpiredErrorPage;
