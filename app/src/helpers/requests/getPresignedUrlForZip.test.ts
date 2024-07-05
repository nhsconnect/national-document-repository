import axios from 'axios';

import { pollForPresignedUrl, requestJobId } from './getPresignedUrlForZip';
import { endpoints } from '../../types/generic/endpoints';

jest.mock('axios');

const mockedAxios = axios as jest.Mocked<typeof axios>;

const nhsNumber = '9000000009';
const baseUrl = 'http://localhost/test';
const baseHeaders = { 'Content-Type': 'application/json', test: 'test' };

describe('getPresignedUrlForZip', () => {});

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
            status: 'Complete',
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
            nhsNumber,
            jobId: testJobId,
        });

        expect(actual).toEqual(expectedData);
        expect(mockedAxios.get).toHaveBeenCalledWith(gatewayUrl);
    });
});
