import axios, { AxiosError } from 'axios';
import getDocumentSearchResults from './documentSearchResults';
import { SearchResult } from '../../types/generic/searchResult';
import { buildSearchResult } from '../test/testBuilders';

// Mock out all top level functions, such as get, put, delete and post:
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// ...

describe('[GET] getDocumentSearchResults', () => {
    test('Document search results handles a 2XX response', async () => {
        const searchResult = buildSearchResult();
        const mockResults = [searchResult];
        mockedAxios.get.mockImplementation(() =>
            Promise.resolve({ status: 200, data: mockResults }),
        );
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
        expect(response).toBeInstanceOf(Array);
        expect(response).toHaveLength(1);

        const data = response as SearchResult[];
        expect(data[0]).toHaveProperty('fileName');
        expect(data[0].fileName).toBe(searchResult.fileName);
        expect(data[0]).toHaveProperty('created');
        expect(data[0].created).toBe(searchResult.created);
        expect(data[0]).toHaveProperty('virusScannerResult');
        expect(data[0].virusScannerResult).toBe(searchResult.virusScannerResult);
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

        expect(response).not.toBeInstanceOf(Array);
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

        expect(response).not.toBeInstanceOf(Array);
        expect(response).toHaveProperty('status');

        const { status } = response as AxiosError;
        expect(status).toBe(500);
    });
});
