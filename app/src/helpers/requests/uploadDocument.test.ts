import axios, { AxiosError } from 'axios';
import {
    buildDocument,
    buildLgFile,
    buildTextFile,
    buildUploadSession,
} from '../test/testBuilders';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    DOCUMENT_UPLOAD_STATE as documentUploadStates,
} from '../../types/pages/UploadDocumentsPage/types';
import {
    UpdateStateArgs,
    updateDocumentState,
    virusScan,
    uploadConfirmation,
    uploadDocumentToS3,
} from './uploadDocuments';
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

describe('uploadDocumentToS3', () => {
    const testFile = buildLgFile(1, 3, 'John Doe');
    const testDocument = buildDocument(
        testFile,
        DOCUMENT_UPLOAD_STATE.SELECTED,
        DOCUMENT_TYPE.LLOYD_GEORGE,
    );
    const mockUploadSession = buildUploadSession([testDocument]);
    const mockSetDocuments = jest.fn();

    it('make POST request to s3 bucket', async () => {
        await uploadDocumentToS3({
            setDocuments: mockSetDocuments,
            uploadSession: mockUploadSession,
            document: testDocument,
        });

        expect(mockedAxios.post).toHaveBeenCalledTimes(1);
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

        const result = await virusScan(virusScanArgs);

        expect(result).toEqual(documentUploadStates.CLEAN);
        expect(mockedWaitForSeconds).not.toBeCalled();
    });

    it('return INFECTED if virus scan api call result was unclean', async () => {
        mockedAxios.post.mockRejectedValueOnce(uncleanResponse);

        const result = await virusScan(virusScanArgs);

        expect(result).toEqual(documentUploadStates.INFECTED);
        expect(mockedWaitForSeconds).not.toBeCalled();
    });

    it('retry up to 3 times if virus scan api call timed out', async () => {
        mockedAxios.post
            .mockRejectedValueOnce(gatewayTimeoutResponse)
            .mockRejectedValueOnce(gatewayTimeoutResponse)
            .mockResolvedValueOnce(cleanResponse);

        const delay_between_retry_in_seconds = 0;

        const result = await virusScan(virusScanArgs);

        expect(result).toEqual(documentUploadStates.CLEAN);

        expect(mockedAxios.post).toBeCalledTimes(3);
        expect(mockedWaitForSeconds).toBeCalledTimes(2);
        expect(mockedWaitForSeconds).toHaveBeenCalledWith(delay_between_retry_in_seconds);
    });

    it('throw an error if timed out for 3 times', async () => {
        mockedAxios.post.mockRejectedValue(gatewayTimeoutResponse);

        await expect(virusScan(virusScanArgs)).rejects.toThrowError(
            'Virus scan api calls timed-out for 3 attempts.',
        );

        expect(mockedAxios.post).toBeCalledTimes(3);
        expect(mockedWaitForSeconds).toBeCalledTimes(3);
    });
});

describe('uploadConfirmation', () => {
    const mockDocuments = [
        {
            file: buildTextFile('file_one', 100),
            state: DOCUMENT_UPLOAD_STATE.SCANNING,
            id: '1',
            progress: 50,
            docType: DOCUMENT_TYPE.LLOYD_GEORGE,
            attempts: 0,
        },
        {
            file: buildTextFile('file_two', 100),
            state: DOCUMENT_UPLOAD_STATE.SCANNING,
            id: '2',
            progress: 50,
            docType: DOCUMENT_TYPE.LLOYD_GEORGE,
            attempts: 0,
        },
    ];
    const uploadConfirmationArgs = {
        nhsNumber: 'mock_nhs_number',
        baseUrl: '/test',
        baseHeaders: { 'Content-Type': 'application/json', test: 'test' },
        documents: mockDocuments,
        uploadSession: buildUploadSession(mockDocuments),
    };

    const succeedResponse = { status: 200 };
    const mockError = new Error('bad request');

    it('return SUCCEED if upload confirmation call was successful', async () => {
        mockedAxios.post.mockResolvedValueOnce(succeedResponse);
        const result = await uploadConfirmation(uploadConfirmationArgs);

        expect(result).toEqual(documentUploadStates.SUCCEEDED);
    });

    it('throw error if upload confirmation call failed', async () => {
        mockedAxios.post.mockRejectedValueOnce(mockError);
        await expect(uploadConfirmation(uploadConfirmationArgs)).rejects.toThrowError(mockError);
    });
});
