import { useEffect } from 'react';
import getAuthToken from '../../helpers/requests/getAuthToken';
import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';

type Props = {};

const AuthCallbackPage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    useEffect(() => {
        const urlSearchParams = new URLSearchParams(window.location.search);
        const code = urlSearchParams.get('code');
        const state = urlSearchParams.get('state');
        if (code && state) {
            void getAuthToken({ baseUrl, code, state });
        }
    });

    return <div> CALLBACK WEEEE</div>;
};

export default AuthCallbackPage;
