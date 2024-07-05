import axios from 'axios';

import getPresignedUrlForZip, {
    pollForPresignedUrl,
    requestJobId,
    ThreePendingErrorMessage,
} from './getPresignedUrlForZip';
import { endpoints } from '../../types/generic/endpoints';
import { JOB_STATUS } from '../../types/generic/downloadManifestJobStatus';

jest.mock('axios');

const mockedAxios = axios as jest.Mocked<typeof axios>;

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
            status: JOB_STATUS.PROCESSING,
            url: expectedPresignedUrl,
        },
    };

    const mockCompletedResponse = {
        statusCode: 200,
        data: {
            status: JOB_STATUS.COMPLETED,
            url: expectedPresignedUrl,
        },
    };

    const mockPendingResponse = {
        statusCode: 200,
        data: {
            status: JOB_STATUS.PENDING,
        },
    };

    it('returns a presigned url', async () => {
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

    it('throw an error if got pending status for 3 times', async () => {
        mockedAxios.post.mockResolvedValueOnce(mockJobIdResponse);
        mockedAxios.get
            .mockResolvedValueOnce(mockPendingResponse)
            .mockResolvedValueOnce(mockPendingResponse)
            .mockResolvedValueOnce(mockPendingResponse);

        await expect(
            getPresignedUrlForZip({ nhsNumber, baseHeaders, baseUrl }),
        ).rejects.toThrowError(ThreePendingErrorMessage);
    });
});

describe('requestJobId', () => {
    it('returns a jobId from backend', async () => {
        const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;
        const expectedJobId = 'jobId2';
        const mockResponse = {
            statusCode: 200,
            data: { jobId: expectedJobId },
        };
        mockedAxios.post.mockResolvedValueOnce(mockResponse);

        const actual = await requestJobId({ baseUrl, nhsNumber, baseHeaders });

        expect(mockedAxios.post).toHaveBeenCalledWith(
            gatewayUrl,
            '',
            expect.objectContaining({
                headers: baseHeaders,
                params: expect.objectContaining({ patientId: nhsNumber }),
            }),
        );

        expect(actual).toEqual(expectedJobId);
    });
});

describe('pollForPresignedUrl', () => {
    it('returns a response from backend', async () => {
        const gatewayUrl = baseUrl + endpoints.DOCUMENT_PRESIGN;
        const testJobId = 'jobId123';
        const expectedData = {
            status: 'Completed',
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
