import axios, { AxiosError } from 'axios';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { AccessAuditData, AccessAuditType } from '../../types/generic/accessAudit';
import postPatientAccessAudit from './postPatientAccessAudit';
import { describe, expect, it, vi, Mocked } from 'vitest';

vi.mock('axios');
const mockedAxios = axios as Mocked<typeof axios>;
(mockedAxios.post as any) = vi.fn();

describe('postPatientAccessAudit', () => {
    const accessAuditData = {
        Reasons: ['01'],
        OtherReasonText: '',
    } as AccessAuditData;

    it('should fetch the report url from the API', async () => {
        mockedAxios.post.mockImplementation(() => Promise.resolve({ status: 200 }));
        const args = {
            accessAuditData,
            accessAuditType: AccessAuditType.deceasedPatient,
            baseUrl: 'http://example.com',
            baseHeaders: {
                'Content-Type': '',
                Authorization: 'token',
            } as AuthHeaders,
            nhsNumber: '1234567890',
        };

        const getSpy = vi.spyOn(mockedAxios, 'post');

        await postPatientAccessAudit(args);

        expect(getSpy).toHaveBeenCalledWith(args.baseUrl + '/AccessAudit', accessAuditData, {
            headers: args.baseHeaders,
            params: {
                accessAuditType: args.accessAuditType,
                patientId: args.nhsNumber,
            },
        });
    });

    it('should return an axios error when the request fails', async () => {
        const postSpy = vi.spyOn(mockedAxios, 'post').mockImplementation(() => {
            throw { response: { status: 404 } };
        });
        const args = {
            accessAuditData,
            accessAuditType: AccessAuditType.deceasedPatient,
            baseUrl: 'http://example.com',
            baseHeaders: {
                'Content-Type': '',
                Authorization: 'token',
            } as AuthHeaders,
            nhsNumber: '1234567890',
        };

        let errorCode;

        try {
            await postPatientAccessAudit(args);
        } catch (e) {
            errorCode = (e as AxiosError)?.response?.status;
        }

        expect(errorCode).not.toBeUndefined();
        expect(errorCode).toBe(404);
        expect(postSpy).toHaveBeenCalledWith(args.baseUrl + '/AccessAudit', accessAuditData, {
            headers: args.baseHeaders,
            params: {
                accessAuditType: args.accessAuditType,
                patientId: args.nhsNumber,
            },
        });
    });
});
