import axios from 'axios';

import { requestJobId } from './getPresignedUrlForZip';
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
