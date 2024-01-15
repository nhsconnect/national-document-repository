import { routes } from '../../types/generic/routes';
import { useNavigate } from 'react-router';
import { ButtonLink } from 'nhsuk-react-components';

const UnauthorisedLoginPage = () => {
    const navigate = useNavigate();

    return (
        <>
            <h1>Your account cannot access this service</h1>
            <p>
                Your account does not have authorisation to view or manage patient records using
                this service.
            </p>
            <h2>Who can access this service</h2>
            <p>
                In order to keep patient information safe, only authorised accounts can access this
                service.
            </p>
            <p> This includes:</p>
            <ul>
                <li>GP practice staff involved in the pilot scheme of this service</li>
                <li>
                    PCSE staff to search or download patient records where there has been an access
                    request
                </li>
            </ul>
            <p>
                If you think you should have access to this service contact the NHS National Service
                Desk.
            </p>
            <ButtonLink
                to="#"
                onClick={(e) => {
                    e.preventDefault();
                    navigate(routes.START);
                }}
            >
                Return to start page
            </ButtonLink>
        </>
    );
};
export default UnauthorisedLoginPage;
