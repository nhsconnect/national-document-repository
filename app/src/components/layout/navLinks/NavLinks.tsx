import React, { useEffect, useState } from 'react';
import type { MouseEvent as ReactEvent } from 'react';
import { Header } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { routes } from '../../../types/generic/routes';
import { useSessionContext } from '../../../providers/sessionProvider/SessionProvider';

const NavLinks = () => {
    const navigate = useNavigate();
    const [session] = useSessionContext();
    const [width, setWidth] = useState<number>(window.innerWidth);
    const nav = (e: ReactEvent<HTMLAnchorElement, MouseEvent>, link: string) => {
        e.preventDefault();
        navigate(link);
    };

    console.log(width);
    useEffect(() => {
        const handleResizeWindow = () => setWidth(window.innerWidth);
        window.addEventListener('resize', handleResizeWindow);
        return () => {
            window.removeEventListener('resize', handleResizeWindow);
        };
    }, []);

    return session.isLoggedIn ? (
        <Header.Nav style={{ display: 'initial', color: 'white' }}>
            <Header.NavItem
                style={{ color: 'white' }}
                role="link"
                className="clickable"
                onClick={(e) => nav(e, routes.START)}
            >
                Home
            </Header.NavItem>
            {width <= 990 ? (
                <>
                    <Header.NavItem
                        role="link"
                        className="clickable"
                        style={{ color: 'white' }}
                        data-testid="search-btn"
                        onClick={(e) => nav(e, routes.SEARCH_PATIENT)}
                    >
                        Search For A Patient
                    </Header.NavItem>
                    <Header.NavItem
                        role="link"
                        className="clickable"
                        style={{ color: 'white' }}
                        data-testid="logout-btn"
                        onClick={(e) => nav(e, routes.LOGOUT)}
                    >
                        Log Out
                    </Header.NavItem>
                </>
            ) : (
                <div style={{ display: 'flex', flexFlow: 'row nowrap' }}>
                    <Header.NavItem
                        role="link"
                        className="clickable"
                        style={{ margin: '0 2rem' }}
                        data-testid="search-btn"
                        onClick={(e) => nav(e, routes.SEARCH_PATIENT)}
                    >
                        Search For A Patient
                    </Header.NavItem>
                    <Header.NavItem
                        role="link"
                        className="clickable"
                        style={{ margin: '0 2rem' }}
                        data-testid="logout-btn"
                        onClick={(e) => nav(e, routes.LOGOUT)}
                    >
                        Log Out
                    </Header.NavItem>
                </div>
            )}
        </Header.Nav>
    ) : null;
};

export default NavLinks;
