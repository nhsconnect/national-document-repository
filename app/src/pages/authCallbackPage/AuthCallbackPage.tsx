import { useEffect } from 'react';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    useEffect(() => {
        const urlSearchParams = new URLSearchParams(window.location.search);
        const code = urlSearchParams.get('code');
        const state = urlSearchParams.get('state');
    });

    return <div> CALLBACK WEEEE</div>;
};

export default AuthCallbackPage;
