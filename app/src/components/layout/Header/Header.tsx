import React from 'react';
import { Header as NhsHeader } from 'nhsuk-react-components';
import NavLinks from '../navLinks/NavLinks';
import { routes } from '../../../types/generic/routes';
import { useNavigate } from 'react-router';

type Props = {};

const Header = (props: Props) => {
  const navigate = useNavigate();
  return (
    <NhsHeader transactional>
      <NhsHeader.Container>
        <NhsHeader.Logo onClick={() => navigate(routes.HOME)} />
        <NhsHeader.ServiceName onClick={() => navigate(routes.HOME)}>
          Inactive Patient Record Administration
        </NhsHeader.ServiceName>
      </NhsHeader.Container>
      <NhsHeader.Nav>
        <NavLinks />
      </NhsHeader.Nav>
    </NhsHeader>
  );
};

export default Header;
