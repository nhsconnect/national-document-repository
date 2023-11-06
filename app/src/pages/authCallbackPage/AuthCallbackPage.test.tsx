import { render, screen, waitFor } from '@testing-library/react';
import AuthCallbackPage from './AuthCallbackPage';
import SessionProvider from '../../providers/sessionProvider/SessionProvider';
import * as ReactRouter from 'react-router';
import { History, createMemoryHistory } from 'history';
import axios from 'axios';
import { buildUserAuth } from '../../helpers/test/testBuilders';
import { routes } from '../../types/generic/routes';
jest.mock('axios');

const mockedAxios = axios as jest.Mocked<typeof axios>;
const params = {
    code: 'cis2-code',
    state: 'cis2-state',
    id: 'cis2-id',
};

const codeAndStateQueryParams = `code=${params.code}&state=${params.state}`;
const allQueryParams = `?${codeAndStateQueryParams}&client_id=${params.id}`;
const baseUiUrl = 'http://localhost:3000' + allQueryParams;
const originalWindowLocation = window.location;

const currentPage = '/example';

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
        const history = createMemoryHistory({
            initialEntries: [currentPage],
            initialIndex: 0,
        });

        mockedAxios.get.mockImplementation(() => Promise.resolve({ data: buildUserAuth() }));
        renderCallbackPage(history);
        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();
        await waitFor(() => {
            expect(history.location.pathname).toBe(routes.UPLOAD_SEARCH);
        });
    });

    it('navigates to the select role page when callback token request is successful', async () => {
        const history = createMemoryHistory({
            initialEntries: [currentPage],
            initialIndex: 0,
        });

        mockedAxios.get.mockImplementation(() => Promise.resolve({ data: buildUserAuth() }));
        renderCallbackPage(history);

        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();
        expect(history.location.pathname).toBe(currentPage);

        await waitFor(() => {
            expect(history.location.pathname).toBe(routes.UPLOAD_SEARCH);
        });
    });

    it('navigates to auth error page when callback token request is unsuccessful', async () => {
        const errorResponse = {
            response: {
                status: 400,
                message: '400 Bad Request',
            },
        };
        const history = createMemoryHistory({
            initialEntries: [currentPage],
            initialIndex: 0,
        });

        mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));
        renderCallbackPage(history);

        expect(screen.getByRole('status')).toBeInTheDocument();
        expect(screen.getByText('Logging in...')).toBeInTheDocument();
        expect(history.location.pathname).toBe(currentPage);

        await waitFor(() => {
            expect(history.location.pathname).toBe(routes.AUTH_ERROR);
        });
    });
});

const renderCallbackPage = (
    history: History = createMemoryHistory({
        initialEntries: [currentPage],
        initialIndex: 1,
    }),
) => {
    render(
        <SessionProvider>
            <ReactRouter.Router navigator={history} location={history.location}>
                <AuthCallbackPage />,
            </ReactRouter.Router>
            ,
        </SessionProvider>,
    );
};
