import React from 'react';
import { Header as NhsHeader } from 'nhsuk-react-components';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router-dom';
import NavLinks from '../navLinks/NavLinks';
import useRole from '../../../helpers/hooks/useRole';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';

type Props = {};

const Header = (props: Props) => {
    const role = useRole();
    const [{ isLoggedIn }] = useSessionContext();
    const navigateHome = () => {
        navigate(!!isLoggedIn ? routes.HOME : routes.START);
    };
    const navigate = useNavigate();
    return (
        <NhsHeader transactional>
            <NhsHeader.Container>
                <NhsHeader.Logo
                    onClick={navigateHome}
                    className="clickable"
                    data-testid="nhs-header-logo"
                    tabIndex={0}
                />
                <NhsHeader.ServiceName onClick={navigateHome} className="clickable" tabIndex={0}>
                    Access and store digital patient documents
                </NhsHeader.ServiceName>
            </NhsHeader.Container>

            <NavLinks data-testid="header-navigation-link" />
        </NhsHeader>
    );
};

export default Header;
