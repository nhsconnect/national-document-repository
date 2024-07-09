import axios from 'axios';

import getPresignedUrlForZip, { pollForPresignedUrl, requestJobId } from './getPresignedUrlForZip';
import { endpoints } from '../../types/generic/endpoints';
import { JOB_STATUS, PollingResponse } from '../../types/generic/downloadManifestJobStatus';
import waitForSeconds from '../utils/waitForSeconds';
import { DOCUMENT_TYPE } from '../../types/pages/UploadDocumentsPage/types';
import { DownloadManifestError } from '../../types/generic/errors';

jest.mock('axios');
jest.mock('../utils/waitForSeconds');

const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockWaitForSeconds = waitForSeconds as jest.MockedFunction<typeof waitForSeconds>;

const nhsNumber = '9000000009';
const baseUrl = 'http://localhost/test';
const baseHeaders = { 'Content-Type': 'application/json', test: 'test' };
const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;

describe('getPresignedUrlForZip', () => {
    const expectedJobId = 'jobId2';
    const expectedPresignedUrl = 'https://s3_test_bucket/filename/abc';
    const mockJobIdResponse = {
        statusCode: 200,
        data: { jobId: expectedJobId },
    };

    const mockProcessingResponse = {
        statusCode: 200,
        data: {
            jobStatus: JOB_STATUS.PROCESSING,
            url: expectedPresignedUrl,
        },
    };

    const mockCompletedResponse = {
        statusCode: 200,
        data: {
            jobStatus: JOB_STATUS.COMPLETED,
            url: expectedPresignedUrl,
        },
    };

    const mockPendingResponse = {
        statusCode: 200,
        data: {
            jobStatus: JOB_STATUS.PENDING,
        },
    };

    const mockFailedResponse = {
        statusCode: 200,
        data: {
            jobStatus: JOB_STATUS.FAILED,
        },
    };

    it('returns a presigned url on job complete', async () => {
        mockedAxios.post.mockResolvedValueOnce(mockJobIdResponse);
        mockedAxios.get
            .mockResolvedValueOnce(mockProcessingResponse)
            .mockResolvedValueOnce(mockCompletedResponse);

        const actual = await getPresignedUrlForZip({
            nhsNumber,
            baseHeaders,
            baseUrl,
        });

        expect(actual).toEqual(expectedPresignedUrl);

        expect(mockedAxios.post).toHaveBeenCalled();
        expect(mockedAxios.get).toHaveBeenCalledWith(
            gatewayUrl,
            expect.objectContaining({
                headers: baseHeaders,
                params: expect.objectContaining({ jobId: expectedJobId }),
            }),
        );
    });

    it('wait for 10 secs before the 1st polling', async () => {
        mockedAxios.post.mockResolvedValueOnce(mockJobIdResponse);
        mockedAxios.get.mockResolvedValueOnce(mockCompletedResponse);

        await getPresignedUrlForZip({
            nhsNumber,
            baseHeaders,
            baseUrl,
        });

        expect(mockWaitForSeconds).toHaveBeenCalledTimes(1);
        expect(mockWaitForSeconds).toHaveBeenCalledWith(10);
    });

    it('wait for 10 secs between every polling', async () => {
        mockedAxios.post.mockResolvedValueOnce(mockJobIdResponse);
        mockedAxios.get
            .mockResolvedValueOnce(mockPendingResponse)
            .mockResolvedValueOnce(mockProcessingResponse)
            .mockResolvedValueOnce(mockProcessingResponse)
            .mockResolvedValueOnce(mockCompletedResponse);

        await getPresignedUrlForZip({
            nhsNumber,
            baseHeaders,
            baseUrl,
        });

        expect(mockWaitForSeconds).toHaveBeenCalledTimes(4);
        expect(mockWaitForSeconds).toHaveBeenCalledWith(10);
    });

    it('throw an error if got pending status for 3 times', async () => {
        mockedAxios.post.mockResolvedValueOnce(mockJobIdResponse);
        mockedAxios.get
            .mockResolvedValueOnce(mockPendingResponse)
            .mockResolvedValueOnce(mockPendingResponse)
            .mockResolvedValueOnce(mockPendingResponse);

        await expect(
            getPresignedUrlForZip({ nhsNumber, baseHeaders, baseUrl }),
        ).rejects.toThrowError(DownloadManifestError);
    });

    it('throw an error if got failed status from api', async () => {
        mockedAxios.post.mockResolvedValueOnce(mockJobIdResponse);
        mockedAxios.get.mockResolvedValueOnce(mockFailedResponse);

        await expect(
            getPresignedUrlForZip({ nhsNumber, baseHeaders, baseUrl }),
        ).rejects.toThrowError(DownloadManifestError);
    });
});

describe('requestJobId', () => {
    const expectedJobId = 'jobId1234';
    const mockJobIdResponse = {
        statusCode: 200,
        data: { jobId: expectedJobId },
    };

    it('returns a jobId from backend', async () => {
        const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;

        mockedAxios.post.mockResolvedValueOnce(mockJobIdResponse);

        const actual = await requestJobId({
            baseUrl,
            nhsNumber,
            baseHeaders,
        });

        expect(mockedAxios.post).toHaveBeenCalledWith(
            gatewayUrl,
            '',
            expect.objectContaining({
                headers: baseHeaders,
                params: expect.objectContaining({
                    patientId: nhsNumber,
                }),
            }),
        );

        expect(actual).toEqual(expectedJobId);
    });

    it('call backend with the correct params for docType and docReferences', async () => {
        const docType = DOCUMENT_TYPE.LLOYD_GEORGE;
        const docReferences = ['doc_id1', 'doc_id2'];

        mockedAxios.post.mockResolvedValueOnce(mockJobIdResponse);

        await requestJobId({
            baseUrl,
            nhsNumber,
            baseHeaders,
            docType,
            docReferences,
        });

        const postRequestParams = mockedAxios.post.mock.calls[0][2]?.params;
        expect(postRequestParams).toEqual({
            docType: 'LG',
            docReferences,
            patientId: nhsNumber,
        });
    });
});

describe('pollForPresignedUrl', () => {
    it('returns a response from backend', async () => {
        const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;
        const testJobId = 'jobId123';
        const expectedData: PollingResponse = {
            jobStatus: JOB_STATUS.COMPLETED,
            url: 'http://test_s3_bucket/file_id',
        };
        const mockResponse = {
            statusCode: 200,
            data: expectedData,
        };

        mockedAxios.get.mockResolvedValueOnce(mockResponse);

        const actual = await pollForPresignedUrl({
            baseHeaders,
            baseUrl,
            jobId: testJobId,
        });

        expect(actual).toEqual(expectedData);
        expect(mockedAxios.get).toHaveBeenCalledWith(
            gatewayUrl,
            expect.objectContaining({
                headers: baseHeaders,
                params: expect.objectContaining({ jobId: testJobId }),
            }),
        );
    });
});
