import { errorToParams } from './errorToParams';
import { AxiosError } from 'axios';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

Date.now = () => new Date('2020-01-01T00:00:00.000Z').getTime();

describe('errorToParams util function', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('returns only interaction_id if error has no err_code', () => {
        const errorResponse = {
            response: {
                status: 500,
                data: { message: '500 Unknown Service Error.' },
            },
        };
        const error = errorResponse as AxiosError;
        expect(errorToParams(error)).toEqual('?encodedError=WyIiLCIxNTc3ODM2ODAwIl0=');
    });

    it('returns param with error code', () => {
        const mockErrorCode = 'test';
        const errorResponse = {
            response: {
                status: 500,
                data: { message: '500 Unknown Service Error.', err_code: mockErrorCode },
            },
        };
        const error = errorResponse as AxiosError;
        const resultErrorToParams = errorToParams(error);
        const errorArray = resultErrorToParams.split('encodedError=');
        const [errorCode] = JSON.parse(atob(errorArray[1]));
        expect(errorCode).toEqual(mockErrorCode);
    });
});
