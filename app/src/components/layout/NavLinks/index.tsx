import React from 'react';
import type { MouseEvent as ReactEvent } from 'react';
import { Header } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';

const NavLinks = () => {
  const isLoggedIn = true;
  const navigate = useNavigate();

  const navigateRoot = (e: ReactEvent<HTMLAnchorElement, MouseEvent>) => {
    e.preventDefault();
    navigate('/');
  };

  return isLoggedIn ? (
    <>
      <Header.NavItem onClick={navigateRoot}>Home</Header.NavItem>
    </>
  ) : null;
};

export default NavLinks;
