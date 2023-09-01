import React from 'react';
import { Header as NhsHeader } from 'nhsuk-react-components';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router';
import NavLinks from '../navLinks/NavLinks';

type Props = {};

const Header = (props: Props) => {
    const navigateHome = () => {
        navigate(routes.HOME);
    };
    const navigate = useNavigate();
    return (
        <NhsHeader transactional>
            <NhsHeader.Container>
                <NhsHeader.Logo onClick={navigateHome} />
                <NhsHeader.ServiceName onClick={navigateHome}>
                    Inactive Patient Record Administration
                </NhsHeader.ServiceName>
            </NhsHeader.Container>

            <NavLinks />
        </NhsHeader>
    );
};

export default Header;
