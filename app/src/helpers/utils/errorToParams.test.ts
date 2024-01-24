import { errorToParams } from './errorToParams';
import { AxiosError } from 'axios';
import { unixTimestamp } from './createTimestamp';

describe('errorToParams util function', () => {
    it('returns only interaction_id if error has no err_code', () => {
        const errorResponse = {
            response: {
                status: 500,
                data: { message: '500 Unknown Service Error.' },
            },
        };
        const error = errorResponse as AxiosError;
        expect(errorToParams(error)).toContain('?encodedError=');
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
        const [errorCode, interactionId] = JSON.parse(atob(errorArray[1]));
        expect(errorCode).toEqual(mockErrorCode);
    });
});
