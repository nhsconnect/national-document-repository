import React from 'react';
import { routes } from '../../types/generic/routes';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
    return (
        <>
            <h1>Page not found</h1>
            <p>
                The page you were looking for could not be found. It might not exist, or you do not
                have access to it.
            </p>
            <Link to={routes.START}>Return home</Link>
        </>
    );
};
export default NotFoundPage;
