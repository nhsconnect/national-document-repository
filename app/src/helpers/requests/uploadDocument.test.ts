import axios, { AxiosError } from 'axios';
import { buildDocument, buildTextFile } from '../test/testBuilders';
import { DOCUMENT_UPLOAD_STATE as documentUploadStates } from '../../types/pages/UploadDocumentsPage/types';
import { UpdateStateArgs, updateDocumentState, virusScanResult } from './uploadDocuments';
import waitForSeconds from '../utils/waitForSeconds';

// Mock out all top level functions, such as get, put, delete and post:
jest.mock('axios');
jest.mock('../utils/waitForSeconds');

const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedWaitForSeconds = waitForSeconds as jest.Mocked<typeof waitForSeconds>;

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

describe('virusScanResult', () => {
    const virusScanArgs = {
        documentReference: 'mock_doc_id',
        baseUrl: '/test',
        baseHeaders: { 'Content-Type': 'application/json', test: 'test' },
    };
    const cleanResponse = { status: 200 };
    const uncleanResponse = { response: { status: 400 } };
    const gatewayTimeoutResponse = { response: { status: 504 } };

    it('return CLEAN if virus scan api call result was clean', async () => {
        mockedAxios.post.mockResolvedValueOnce(cleanResponse);

        const result = await virusScanResult(virusScanArgs);

        expect(result).toEqual(documentUploadStates.CLEAN);
        expect(mockedWaitForSeconds).not.toBeCalled();
    });

    it('return INFECTED if virus scan api call result was unclean', async () => {
        mockedAxios.post.mockRejectedValueOnce(uncleanResponse);

        const result = await virusScanResult(virusScanArgs);

        expect(result).toEqual(documentUploadStates.INFECTED);
        expect(mockedWaitForSeconds).not.toBeCalled();
    });

    it('retry up to 3 times if virus scan api call timed out', async () => {
        mockedAxios.post
            .mockRejectedValueOnce(gatewayTimeoutResponse)
            .mockRejectedValueOnce(gatewayTimeoutResponse)
            .mockResolvedValueOnce(cleanResponse);

        const delay_between_retry_in_seconds = 5;

        const result = await virusScanResult(virusScanArgs);

        expect(result).toEqual(documentUploadStates.CLEAN);

        expect(mockedAxios.post).toBeCalledTimes(3);
        expect(mockedWaitForSeconds).toBeCalledTimes(2);
        expect(mockedWaitForSeconds).toHaveBeenCalledWith(delay_between_retry_in_seconds);
    });

    it('throw an error if timed out for 3 times', async () => {
        mockedAxios.post.mockRejectedValue(gatewayTimeoutResponse);

        await expect(virusScanResult(virusScanArgs)).rejects.toThrowError(
            'Virus scan api calls timed-out for 3 attempts.',
        );

        expect(mockedAxios.post).toBeCalledTimes(3);
        expect(mockedWaitForSeconds).toBeCalledTimes(3);
    });
});
