import { render, screen, waitFor } from '@testing-library/react';
import NavLinks from './NavLinks';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../types/generic/routes';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('NavLinks', () => {
    const oldWindowLocation = window.location.href;
    beforeEach(() => {
        localStorage.setItem('UserSession', '');
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
        window.location.href = oldWindowLocation;
    });

    describe('Rendering', () => {
        it('renders a navlink for app home when user logged in', () => {
            const isLoggedIn = true;
            renderNav(isLoggedIn);

            expect(screen.getByRole('link', { name: 'Home' })).toBeInTheDocument();
        });

        it('renders a navlink for app logout when user logged in', () => {
            const isLoggedIn = true;
            renderNav(isLoggedIn);

            expect(screen.getByRole('link', { name: 'Sign out' })).toBeInTheDocument();
        });

        it('renders a navlink for app searcg when user logged in', () => {
            const isLoggedIn = true;
            renderNav(isLoggedIn);

            expect(screen.getByRole('link', { name: 'Search for a patient' })).toBeInTheDocument();
        });

        it('does not render a navlink for app home when user logged out', () => {
            const isLoggedIn = false;
            renderNav(isLoggedIn);

            expect(screen.queryByRole('link', { name: 'Home' })).not.toBeInTheDocument();
        });

        it('does not render a navlink for app home search user logged out', () => {
            const isLoggedIn = false;
            renderNav(isLoggedIn);

            expect(
                screen.queryByRole('link', { name: 'Search for a patient' }),
            ).not.toBeInTheDocument();
        });

        it('does not render a navlink for app logout when user logged out', () => {
            const isLoggedIn = false;
            renderNav(isLoggedIn);

            expect(screen.queryByRole('link', { name: 'Sign out' })).not.toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates to app home when home link is clicked', async () => {
            const isLoggedIn = true;
            renderNav(isLoggedIn);

            const homeLink = screen.getByRole('link', { name: 'Home' });
            expect(homeLink).toBeInTheDocument();

            await userEvent.click(homeLink);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
            });
        });

        it('navigates to app search when search link is clicked', async () => {
            const isLoggedIn = true;
            renderNav(isLoggedIn);

            const searchLink = screen.getByRole('link', { name: 'Search for a patient' });
            expect(searchLink).toBeInTheDocument();

            await userEvent.click(searchLink);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
            });
        });

        it('navigates to app logout when logout link is clicked', async () => {
            const isLoggedIn = true;
            renderNav(isLoggedIn);

            const logoutLink = screen.getByRole('link', { name: 'Sign out' });
            expect(logoutLink).toBeInTheDocument();

            await userEvent.click(logoutLink);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.LOGOUT);
            });
        });
    });
});

const renderNav = (isLoggedIn: boolean) => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };
    render(
        <SessionProvider sessionOverride={isLoggedIn ? auth : undefined}>
            <NavLinks />
        </SessionProvider>,
    );
};
