import { render, screen, waitFor } from '@testing-library/react';
import AuthCallbackPage from './AuthCallbackPage';
import SessionProvider, { Session } from '../../providers/sessionProvider/SessionProvider';
import axios from 'axios';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import { routes } from '../../types/generic/routes';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';

const mockedUseNavigate = jest.fn();
jest.mock('axios');
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
const mockedAxios = axios as jest.Mocked<typeof axios>;
const params = {
    code: 'cis2-code',
    state: 'cis2-state',
    id: 'cis2-id',
};

const codeAndStateQueryParams = `code=${params.code}&state=${params.state}`;
const allQueryParams = `?${codeAndStateQueryParams}&client_id=${params.id}`;
const baseUiUrl = 'http://localhost' + allQueryParams;
const originalWindowLocation = window.location;

describe('AuthCallbackPage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';

        Object.defineProperty(window, 'location', {
            configurable: true,
            enumerable: true,
            value: new URL(baseUiUrl),
        });
        window.sessionStorage.clear();
    });
    afterEach(() => {
        jest.clearAllMocks();
        window.sessionStorage.clear();
        Object.defineProperty(window, 'location', {
            configurable: true,
            enumerable: true,
            value: originalWindowLocation,
        });
    });

    it('returns a loading state until redirection to token request handler', async () => {
        mockedAxios.get.mockImplementation(() => Promise.resolve({ data: buildUserAuth() }));
        renderCallbackPage();
        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UPLOAD_SEARCH);
        });
    });

    it('navigates to the select role page when callback token request is successful', async () => {
        mockedAxios.get.mockImplementation(() => Promise.resolve({ data: buildUserAuth() }));
        renderCallbackPage();

        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UPLOAD_SEARCH);
        });
    });

    it('navigates to DOWNLOAD_SEARCH when callback token request is successful and user role is PCSE', async () => {
        mockedAxios.get.mockImplementationOnce(() =>
            Promise.resolve({
                data: buildUserAuth({ role: REPOSITORY_ROLE.PCSE }),
            }),
        );
        renderCallbackPage();

        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.DOWNLOAD_SEARCH);
        });
    });

    it('display non-BSOL landing page when user role is GP and isBSOL is false', async () => {
        mockedAxios.get.mockImplementationOnce(() =>
            Promise.resolve({ data: buildUserAuth({ isBSOL: false }) }),
        );
        renderCallbackPage();

        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();

        await waitFor(() => {
            expect(
                screen.getByText('You’re outside of Birmingham and Solihull (BSOL)'),
            ).toBeInTheDocument();
        });
    });

    it('navigates to auth error page when callback token request is unsuccessful', async () => {
        const errorResponse = {
            response: {
                status: 400,
                message: '400 Bad Request',
            },
        };

        mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));
        renderCallbackPage();

        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.AUTH_ERROR);
        });
    });
});

const renderCallbackPage = () => {
    render(
        <SessionProvider>
            <AuthCallbackPage />
        </SessionProvider>,
    );
};
