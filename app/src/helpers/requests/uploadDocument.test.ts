import axios, { AxiosError } from 'axios';
import { buildDocument, buildTextFile } from '../test/testBuilders';
import { DOCUMENT_UPLOAD_STATE as documentUploadStates } from '../../types/pages/UploadDocumentsPage/types';
import { UpdateStateArgs, updateDocumentState } from './uploadDocuments';

// Mock out all top level functions, such as get, put, delete and post:
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('[POST] updateDocumentState', () => {
    test('updateDocumentState handles a 2XX response', async () => {
        const documents = [buildDocument(buildTextFile('test1'), documentUploadStates.SUCCEEDED)];
        mockedAxios.post.mockImplementation(() => Promise.resolve({ status: 200 }));
        const args: UpdateStateArgs = {
            documents,
            uploadingState: true,
            baseUrl: '/test',
            baseHeaders: { 'Content-Type': 'application/json', test: 'test' },
        };

        const error = AxiosError;

        expect(() => updateDocumentState(args)).not.toThrow(error);
    });
});
