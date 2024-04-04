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

    useEffect(() => {
        const handleResizeWindow = () => setWidth(window.innerWidth);
        window.addEventListener('resize', handleResizeWindow);
        return () => {
            window.removeEventListener('resize', handleResizeWindow);
        };
    }, []);

    const appLinks = [
        { href: routes.SEARCH_PATIENT, label: 'Search For A Patient', id: 'search-btn' },
        { href: routes.LOGOUT, label: 'Log Out', id: 'logout-btn' },
    ];

    return session.isLoggedIn ? (
        <Header.Nav style={{ display: 'initial', color: 'white' }} className="navlinks">
            <Header.NavItem
                className="navlinks_item clickable"
                style={{ color: 'white' }}
                role="link"
                onClick={(e) => nav(e, routes.START)}
            >
                Home
            </Header.NavItem>
            {width <= 990 ? (
                <>
                    {appLinks.map((l) => (
                        <Header.NavItem
                            className="navlinks_item navlinks_item--mobile clickable"
                            key={l.href}
                            role="link"
                            data-testid={l.id}
                            onClick={(e) => nav(e, l.href)}
                        >
                            {l.label}
                        </Header.NavItem>
                    ))}
                </>
            ) : (
                <div style={{ display: 'flex', flexFlow: 'row nowrap' }}>
                    {appLinks.map((l) => (
                        <Header.NavItem
                            className="navlinks_item clickable"
                            key={l.href}
                            style={{ margin: '0 2rem' }}
                            role="link"
                            data-testid={l.id}
                            onClick={(e) => nav(e, l.href)}
                        >
                            {l.label}
                        </Header.NavItem>
                    ))}
                </div>
            )}
        </Header.Nav>
    ) : null;
};

export default NavLinks;
