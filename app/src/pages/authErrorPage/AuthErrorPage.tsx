import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import { MouseEvent, useState } from 'react';
import { endpoints } from '../../types/generic/endpoints';
import Spinner from '../../components/generic/spinner/Spinner';
import { Link } from 'react-router-dom';

const AuthErrorPage = () => {
    const baseAPIUrl = useBaseAPIUrl();
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = (e: MouseEvent<HTMLAnchorElement>) => {
        setIsLoading(true);
        e.preventDefault();
        window.location.replace(`${baseAPIUrl}${endpoints.LOGIN}`);
    };
    return !isLoading ? (
        <>
            <h1>You have been logged out</h1>
            <p>
                If you were entering information, it has not been saved and you will need to
                re-enter it.
            </p>
            <p>
                If the issue persists please contact the{' '}
                <a
                    href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                    target="_blank"
                    rel="noreferrer"
                >
                    NHS National Service Desk
                </a>
                .
            </p>
            <Link to="" onClick={handleLogin}>
                Log in
            </Link>
        </>
    ) : (
        <Spinner status="Logging in..." />
    );
};
export default AuthErrorPage;
