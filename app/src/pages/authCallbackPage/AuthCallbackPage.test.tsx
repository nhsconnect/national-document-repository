import { render, screen, waitFor } from '@testing-library/react';
import AuthCallbackPage from './AuthCallbackPage';
import SessionProvider from '../../providers/sessionProvider/SessionProvider';
import axios from 'axios';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import { routes } from '../../types/generic/routes';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { UserAuth } from '../../types/blocks/userAuth';

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
    });
    afterEach(() => {
        jest.clearAllMocks();
        Object.defineProperty(window, 'location', {
            configurable: true,
            enumerable: true,
            value: originalWindowLocation,
        });
    });

    it('returns a loading state until redirection to token request handler', async () => {
        mockedAxios.get.mockImplementation(() =>
            Promise.resolve({ data: buildUserAuth({ isBSOL: true }) }),
        );
        renderCallbackPage();
        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UPLOAD_SEARCH);
        });
    });

    const testCases: Array<[Partial<UserAuth>, routes]> = [
        [{ isBSOL: true, role: REPOSITORY_ROLE.GP_ADMIN }, routes.UPLOAD_SEARCH],
        [{ isBSOL: false, role: REPOSITORY_ROLE.GP_ADMIN }, routes.NON_BSOL_LANDING],
        [{ isBSOL: false, role: REPOSITORY_ROLE.GP_CLINICAL }, routes.UPLOAD_SEARCH],
        [{ isBSOL: false, role: REPOSITORY_ROLE.PCSE }, routes.DOWNLOAD_SEARCH],
        // below two cases are not supposed to happen in current implementation, but anyway check that they don't cause odd result
        [{ isBSOL: true, role: REPOSITORY_ROLE.GP_CLINICAL }, routes.UPLOAD_SEARCH],
        [{ isBSOL: true, role: REPOSITORY_ROLE.PCSE }, routes.DOWNLOAD_SEARCH],
    ];

    it.each(testCases)(
        'navigates to the correct search patient page according to user role, case: %p',
        async (authOverride, expectedRoute) => {
            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({
                    data: buildUserAuth(authOverride),
                }),
            );
            renderCallbackPage();

            expect(screen.getByRole('status')).toBeInTheDocument();
            expect(screen.getByText('Logging in...')).toBeInTheDocument();

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(expectedRoute);
            });
        },
    );

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
