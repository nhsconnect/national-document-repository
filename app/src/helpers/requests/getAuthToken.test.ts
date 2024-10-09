import axios, { AxiosError } from 'axios';
import { buildUserAuth } from '../test/testBuilders';
import { UserAuth } from '../../types/blocks/userAuth';
import getAuthToken from './getAuthToken';
// Mock out all top level functions, such as get, put, delete and post:
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// ...

describe('[GET] getAuthToken', () => {
    const args = {
        code: 'xx',
        state: 'xx',
        axios,
    };

    test('getAuthToken handles a 2XX response', async () => {
        const mockAuth = buildUserAuth();
        mockedAxios.get.mockImplementation(() => Promise.resolve({ status: 200, data: mockAuth }));

        let response: UserAuth | AxiosError;
        try {
            response = await getAuthToken(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }
        expect(response).not.toHaveProperty('status');
        expect(response).toHaveProperty('authorisation_token');
        expect(response).toHaveProperty('role');

        const data = response as UserAuth;
        expect(data.authorisation_token).toBe(mockAuth.authorisation_token);
        expect(data.role).toBe(mockAuth.role);
    });

    test('getAuthToken catches a 4XX response', async () => {
        mockedAxios.get.mockImplementation(() => Promise.reject({ status: 403 }));
        let response: UserAuth | AxiosError;
        try {
            response = await getAuthToken(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }

        expect(response).not.toHaveProperty('authorisation_token');
        expect(response).not.toHaveProperty('role');
        expect(response).toHaveProperty('status');

        const { status } = response as AxiosError;
        expect(status).toBe(403);
    });

    test('getAuthToken catches a 5XX response', async () => {
        mockedAxios.get.mockImplementation(() => Promise.reject({ status: 500 }));
        let response: UserAuth | AxiosError;
        try {
            response = await getAuthToken(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }

        expect(response).not.toHaveProperty('authorisation_token');
        expect(response).not.toHaveProperty('role');
        expect(response).toHaveProperty('status');

        const { status } = response as AxiosError;
        expect(status).toBe(500);
    });
});
