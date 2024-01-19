import React, { MouseEvent, useState } from 'react';
import { routes } from '../../types/generic/routes';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router';
import { endpoints } from '../../types/generic/endpoints';
import Spinner from '../../components/generic/spinner/Spinner';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';

const UnauthorisedPage = () => {
    const baseAPIUrl = useBaseAPIUrl();
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const handleLogin = (e: MouseEvent<HTMLAnchorElement>) => {
        setIsLoading(true);
        e.preventDefault();
        window.location.replace(`${baseAPIUrl}${endpoints.LOGIN}`);
    };
    return !isLoading ? (
        <>
            <h1>Unauthorised access</h1>
            <p>
                The page you were looking for could not be accessed. If you have the permissions,{' '}
                <Link to="" onClick={handleLogin}>
                    logging in
                </Link>{' '}
                may fix this.
            </p>
            <Link
                to="#"
                onClick={(e) => {
                    e.preventDefault();
                    navigate(routes.START);
                }}
            >
                Return home
            </Link>
        </>
    ) : (
        <Spinner status="Logging in..." />
    );
};
export default UnauthorisedPage;
