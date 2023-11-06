import axios, { AxiosError } from 'axios';
import getDocumentSearchResults from './getDocumentSearchResults';
import { SearchResult } from '../../types/generic/searchResult';
import { buildUserAuth } from '../test/testBuilders';
import { UserAuth } from '../../types/blocks/userAuth';
import getAuthToken from './getAuthToken';

// Mock out all top level functions, such as get, put, delete and post:
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// ...

describe('[GET] getDocumentSearchResults', () => {
    test('Document search results handles a 2XX response', async () => {
        const mockAuth = buildUserAuth();
        mockedAxios.get.mockImplementation(() => Promise.resolve({ status: 200, data: mockAuth }));
        const args = {
            baseUrl: '/test',
            code: 'xx',
            state: 'xx',
        };
        let response: UserAuth | AxiosError;
        try {
            response = await getAuthToken(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }
        expect(response).not.toHaveProperty('status');
        expect(response).toHaveProperty('authorisation_token');
        expect(response).toHaveProperty('organisations');

        const data = response as UserAuth;
        expect(data.authorisation_token).toBe(mockAuth.authorisation_token);
        expect(data.organisations).toBeInstanceOf(Array);
        expect(data.organisations).toHaveLength(1);
        expect(data.organisations[0]).toHaveProperty('role');
        expect(data.organisations[0].role).toBe(mockAuth.organisations[0].role);
    });

    test('Document search results catches a 4XX response', async () => {
        mockedAxios.get.mockImplementation(() => Promise.reject({ status: 403 }));
        const args = {
            nhsNumber: '',
            baseUrl: '/test',
            baseHeaders: { 'Content-Type': 'application/json', test: 'test' },
        };
        let response: SearchResult[] | AxiosError;
        try {
            response = await getDocumentSearchResults(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }

        expect(response).not.toHaveProperty('authorisation_token');
        expect(response).not.toHaveProperty('organisations');
        expect(response).toHaveProperty('status');

        const { status } = response as AxiosError;
        expect(status).toBe(403);
    });

    test('Document search results catches a 5XX response', async () => {
        mockedAxios.get.mockImplementation(() => Promise.reject({ status: 500 }));
        const args = {
            nhsNumber: '',
            baseUrl: '/test',
            baseHeaders: { 'Content-Type': 'application/json', test: 'test' },
        };
        let response: SearchResult[] | AxiosError;
        try {
            response = await getDocumentSearchResults(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }

        expect(response).not.toHaveProperty('authorisation_token');
        expect(response).not.toHaveProperty('organisations');
        expect(response).toHaveProperty('status');

        const { status } = response as AxiosError;
        expect(status).toBe(500);
    });
});
