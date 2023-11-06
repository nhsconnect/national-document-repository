import axios, { AxiosError } from 'axios';
import deleteAllDocuments, { DeleteResponse } from './deleteAllDocuments';
import { DOCUMENT_TYPE } from '../../types/pages/UploadDocumentsPage/types';

// Mock out all top level functions, such as get, put, delete and post:
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// ...

describe('[DELETE] deleteAllDocuments', () => {
    test('Delete all documents handles a 2XX response', async () => {
        mockedAxios.delete.mockImplementation(() => Promise.resolve({ status: 200, data: '' }));
        const args = {
            docType: DOCUMENT_TYPE.ARF,
            nhsNumber: '90000000009',
            baseUrl: '/test',
            baseHeaders: { 'Content-Type': 'application/json', test: 'test' },
        };
        let response: DeleteResponse | AxiosError;
        try {
            response = await deleteAllDocuments(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }
        expect(response).toHaveProperty('status');
        expect(response?.status).toBe(200);
    });

    test('Delete all documents catches a 4XX response', async () => {
        mockedAxios.delete.mockImplementation(() => Promise.reject({ status: 403, data: '' }));
        const args = {
            docType: DOCUMENT_TYPE.ARF,
            nhsNumber: '',
            baseUrl: '/test',
            baseHeaders: { 'Content-Type': 'application/json', test: 'test' },
        };
        let response: DeleteResponse | AxiosError;
        try {
            response = await deleteAllDocuments(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }
        expect(response).toHaveProperty('status');
        expect(response?.status).toBe(403);
    });

    test('Delete all documents catches a 5XX response', async () => {
        mockedAxios.delete.mockImplementation(() => Promise.reject({ status: 500, data: '' }));
        const args = {
            docType: DOCUMENT_TYPE.ARF,
            nhsNumber: '',
            baseUrl: '/test',
            baseHeaders: { 'Content-Type': 'application/json', test: 'test' },
        };
        let response: DeleteResponse | AxiosError;
        try {
            response = await deleteAllDocuments(args);
        } catch (e) {
            const error = e as AxiosError;
            response = error;
        }
        expect(response).toHaveProperty('status');
        expect(response?.status).toBe(500);
    });
});
