import { render, screen, waitFor } from '@testing-library/react';
import LogoutPage from './LogoutPage';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import axios from 'axios';
import { routes } from '../../types/generic/routes';
import { afterEach, beforeEach, describe, expect, it, vi, Mocked } from 'vitest';

vi.mock('axios');
const mockedAxios = axios as Mocked<typeof axios>;
const mockSetSession = vi.fn();
const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockedUseNavigate,
}));

describe('logoutPage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('returns a loading state until logout redirect', () => {
        renderLogoutPage();
        const status = 'Signing out...';
        expect(screen.getByText(status)).toBeInTheDocument();
    });

    it('navigates to the home page when logout is successful', async () => {
        const successResponse = {
            response: {
                status: 200,
            },
        };

        mockedAxios.get.mockImplementation(() => Promise.resolve(successResponse));
        renderLogoutPage();

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.START);
        });
    });

    it('navigates to the previous page when logout fails', async () => {
        const errorResponse = {
            response: {
                status: 500,
            },
        };

        mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));
        renderLogoutPage();

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(-1);
        });
    });

    it('clears the session from session provider', async () => {
        Storage.prototype.setItem = vi.fn();
        const successResponse = {
            response: {
                status: 200,
            },
        };

        mockedAxios.get.mockImplementation(() => Promise.resolve(successResponse));
        renderLogoutPage();

        await waitFor(() => {
            expect(mockSetSession).toHaveBeenCalledWith({
                auth: null,
                isLoggedIn: false,
            });
        });
    });
});

const renderLogoutPage = () => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
    };
    render(
        <SessionProvider sessionOverride={auth} setSessionOverride={mockSetSession}>
            <LogoutPage />
        </SessionProvider>,
    );
};
