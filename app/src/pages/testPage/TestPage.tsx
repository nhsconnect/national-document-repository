import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { routes } from '../../types/generic/routes';

type Props = {};

function TestPage(props: Props) {
    const location = useLocation();
    const value = location.state?.someKey;

    return (
        <>
            <h1>Test page</h1>
            <p>trying call navigate() while passing arbitrary value to dest component</p>
            {value ? <p>received value: {value}</p> : <p>no value received</p>}

            <Link to={routes.START}>Back to start page</Link>
        </>
    );
}

export default TestPage;
