import { render, screen, waitFor } from '@testing-library/react';
import NavLinks from './NavLinks';
import SessionProvider, { Session } from '../../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../../../helpers/test/testBuilders';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../types/generic/routes';

const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('NavLinks', () => {
    const oldWindowLocation = window.location;
    beforeEach(() => {
        sessionStorage.setItem('UserSession', '');
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
        window.location = oldWindowLocation;
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

            expect(screen.getByRole('link', { name: 'Log Out' })).toBeInTheDocument();
        });
        it('does not render a navlink for app home when user logged out', () => {
            const isLoggedIn = false;
            renderNav(isLoggedIn);

            expect(screen.queryByRole('link', { name: 'Home' })).not.toBeInTheDocument();
        });

        it('does not render a navlink for app logout when user logged out', () => {
            const isLoggedIn = false;
            renderNav(isLoggedIn);

            expect(screen.queryByRole('link', { name: 'Log Out' })).not.toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates to app home when home link is clicked', async () => {
            const isLoggedIn = true;
            renderNav(isLoggedIn);

            const homeLink = screen.getByRole('link', { name: 'Home' });
            expect(homeLink).toBeInTheDocument();

            act(() => {
                userEvent.click(homeLink);
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.START);
            });
        });

        it('navigates to app logout when logout link is clicked', async () => {
            const isLoggedIn = true;
            renderNav(isLoggedIn);

            const logoutLink = screen.getByRole('link', { name: 'Log Out' });
            expect(logoutLink).toBeInTheDocument();

            act(() => {
                userEvent.click(logoutLink);
            });

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
