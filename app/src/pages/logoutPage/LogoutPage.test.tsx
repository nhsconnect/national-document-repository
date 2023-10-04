import { render, screen, waitFor } from '@testing-library/react';
import LogoutPage from './LogoutPage';
import { createMemoryHistory } from 'history';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import * as ReactRouter from 'react-router';
import axios from 'axios';
import { routes } from '../../types/generic/routes';
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('logoutPage', () => {
    const currentPage = '/example';
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('returns a loading state until logout redirect', () => {
        renderLogoutPage();
        const status = 'Logging out...';
        expect(screen.getByText(status)).toBeInTheDocument();
    });

    it('navigates to the home page when logout is successful', async () => {
        const history = createMemoryHistory({
            initialEntries: [currentPage],
            initialIndex: 0,
        });
        const func = jest.fn();
        const successResponse = {
            response: {
                status: 200,
            },
        };

        mockedAxios.get.mockImplementation(() => Promise.resolve(successResponse));
        renderLogoutPage(history);
        expect(history.location.pathname).toBe(currentPage);

        await waitFor(() => {
            expect(history.location.pathname).toBe(routes.HOME);
        });
    });

    it('navigates to the previous page when logout fails', async () => {
        const previousPage = '/previous';
        const history = createMemoryHistory({
            initialEntries: [previousPage, currentPage],
            initialIndex: 1,
        });
        const errorResponse = {
            response: {
                status: 500,
            },
        };

        mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));
        renderLogoutPage(history);
        expect(history.location.pathname).toBe(currentPage);

        await waitFor(() => {
            expect(history.location.pathname).toBe(previousPage);
        });
    });

    it('clears the session from session provider', async () => {
        const history = createMemoryHistory({
            initialEntries: [currentPage],
            initialIndex: 0,
        });
        const mockSetSession = jest.fn();
        Storage.prototype.setItem = jest.fn();
        const successResponse = {
            response: {
                status: 200,
            },
        };
        const auth: Session = {
            auth: buildUserAuth(),
            isLoggedIn: true,
        };
        mockedAxios.get.mockImplementation(() => Promise.resolve(successResponse));
        renderLogoutPage(history, auth, mockSetSession);

        await waitFor(() => {
            expect(mockSetSession).toHaveBeenCalledWith({
                auth: null,
                isLoggedIn: false,
            });
        });
    });
});

const renderLogoutPage = (
    history = createMemoryHistory({
        initialEntries: ['/'],
        initialIndex: 0,
    }),
    authOverride?: Partial<Session>,
    setSessionOverride = jest.fn(),
) => {
    const auth: Session = {
        auth: buildUserAuth(),
        isLoggedIn: true,
        ...authOverride,
    };
    render(
        <ReactRouter.Router navigator={history} location={'/'}>
            <SessionProvider sessionOverride={auth} setSessionOverride={setSessionOverride}>
                <LogoutPage />
            </SessionProvider>
        </ReactRouter.Router>,
    );
};
