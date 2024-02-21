import { render, screen, waitFor } from '@testing-library/react';
import AuthCallbackPage from './AuthCallbackPage';
import SessionProvider from '../../providers/sessionProvider/SessionProvider';
import axios from 'axios';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import { routes } from '../../types/generic/routes';
import ConfigProvider from '../../providers/configProvider/ConfigProvider';
import useConfig from '../../helpers/hooks/useConfig';
import useRole from '../../helpers/hooks/useRole';
import { act } from 'react-dom/test-utils';
import { endpoints } from '../../types/generic/endpoints';
import { defaultFeatureFlags } from '../../helpers/requests/getFeatureFlags';

jest.mock('../../helpers/hooks/useConfig');
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
        sessionStorage.setItem('FeatureFlags', '');
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

    describe('Rendering', () => {
        it('returns a loading state until redirection to token request handler', async () => {
            mockedAxios.get.mockImplementation(() => Promise.resolve({ data: buildUserAuth() }));
            act(() => {
                renderCallbackPage();
            });
            expect(screen.getByRole('status')).toBeInTheDocument();
            expect(screen.getByText('Logging in...')).toBeInTheDocument();

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
            });
        });
    });

    describe('Navigation', () => {
        it('navigates to the select role page when callback token request is successful', async () => {
            mockedAxios.get.mockImplementation(() => Promise.resolve({ data: buildUserAuth() }));
            renderCallbackPage();

            expect(screen.getByRole('status')).toBeInTheDocument();
            expect(screen.getByText('Logging in...')).toBeInTheDocument();

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.HOME);
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
        it('navigates to unauthorised login page when callback token request is 401', async () => {
            const errorResponse = {
                response: {
                    status: 401,
                    message: '401 Unauthorised',
                },
            };

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));
            renderCallbackPage();

            expect(screen.getByRole('status')).toBeInTheDocument();
            expect(screen.getByText('Logging in...')).toBeInTheDocument();

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.UNAUTHORISED_LOGIN);
            });
        });
    });

    describe('Config', () => {
        it('sets session context to user is has a role', async () => {
            mockedAxios.get.mockImplementation(() => Promise.resolve({ data: buildUserAuth() }));
            renderCallbackPage();
            await waitFor(() => {
                expect(screen.getByText('LOGGEDIN: true')).toBeInTheDocument();
            });
        });
        it('sets config context to user is has feature flags', async () => {
            mockedAxios.get.mockImplementation((url) => {
                if (url.includes(endpoints.AUTH)) {
                    return Promise.resolve({ data: buildUserAuth() });
                } else {
                    return Promise.resolve({
                        data: { ...defaultFeatureFlags, testFeature1: true },
                    });
                }
            });
            renderCallbackPage();
            await waitFor(() => {
                expect(screen.getByText('FLAG: true')).toBeInTheDocument();
            });
        });
    });
});

const TestApp = () => {
    const config = useConfig();
    const role = useRole();
    return (
        <div>
            <div>{`FLAG: ${config.featureFlags.testFeature1}`.normalize()}</div>;
            <div>{`LOGGEDIN: ${!!role}`.normalize()}</div>;
            <AuthCallbackPage />;
        </div>
    );
};

const renderCallbackPage = () => {
    render(
        <SessionProvider>
            <ConfigProvider>
                <TestApp />
            </ConfigProvider>
        </SessionProvider>,
    );
};
