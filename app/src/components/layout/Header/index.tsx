import React from 'react';
import { Header as NhsHeader } from 'nhsuk-react-components';
import NavLinks from '../NavLinks';

type Props = {};

function Header(props: Props) {
  return (
    <NhsHeader transactional>
      <NhsHeader.Container>
        <NhsHeader.Logo />
        <NhsHeader.ServiceName>
          Inactive Patient Record Administration
        </NhsHeader.ServiceName>
      </NhsHeader.Container>
      <NhsHeader.Nav>
        <NavLinks />
      </NhsHeader.Nav>
    </NhsHeader>
  );
}

export default Header;
