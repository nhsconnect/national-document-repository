import axios, { AxiosError } from 'axios';
import downloadReport from './downloadReport';
import { ReportData } from '../../types/generic/reports';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { describe, expect, it, vi, Mocked } from 'vitest';

vi.mock('axios');
const mockedAxios = axios as Mocked<typeof axios>;

describe('downloadReport', () => {
    const report = {
        endpoint: '/download',
    } as ReportData;

    it('should fetch the report url from the API', async () => {
        mockedAxios.get.mockImplementation(() =>
            Promise.resolve({ status: 200, data: { url: 'downloadFile' } }),
        );
        const args = {
            report,
            fileType: 'csv',
            baseUrl: 'http://example.com',
            baseHeaders: {
                'Content-Type': '',
                Authorization: 'token',
            } as AuthHeaders,
        };

        const getSpy = vi.spyOn(mockedAxios, 'get');

        await downloadReport(args);

        expect(getSpy).toHaveBeenCalledWith(args.baseUrl + report.endpoint, {
            headers: args.baseHeaders,
            params: { outputFileFormat: args.fileType },
        });
    });

    it('should throw an axios error when the request fails', async () => {
        mockedAxios.get.mockImplementation(() => {
            throw { response: { status: 404 } };
        });
        const args = {
            report,
            fileType: 'csv',
            baseUrl: 'http://example.com',
            baseHeaders: {
                'Content-Type': '',
                Authorization: 'token',
            } as AuthHeaders,
        };

        const getSpy = vi.spyOn(mockedAxios, 'get');
        let errorCode;

        try {
            await downloadReport(args);
        } catch (e) {
            errorCode = (e as AxiosError)?.response?.status;
        }

        expect(errorCode).not.toBeUndefined();
        expect(errorCode).toBe(404);
        expect(getSpy).toHaveBeenCalledWith(args.baseUrl + report.endpoint, {
            headers: args.baseHeaders,
            params: { outputFileFormat: args.fileType },
        });
    });
});
