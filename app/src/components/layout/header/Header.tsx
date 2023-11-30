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
                <NhsHeader.Logo onClick={navigateHome} className="clickable" />
                <NhsHeader.ServiceName onClick={navigateHome} className="clickable">
                    Access and store digital GP records
                </NhsHeader.ServiceName>
            </NhsHeader.Container>

            <NavLinks />
        </NhsHeader>
    );
};

export default Header;
