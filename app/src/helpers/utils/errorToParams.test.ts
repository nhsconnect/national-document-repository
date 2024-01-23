import { errorToParams } from './errorToParams';
import { AxiosError } from 'axios';

test('returns empty string param if error has no err_code', () => {
    const errorResponse = {
        response: {
            status: 500,
            data: { message: '500 Unknown Service Error.' },
        },
    };
    const error = errorResponse as AxiosError;

    expect(errorToParams(error)).toBe('');
});

test('returns param with error code', () => {
    const errorResponse = {
        response: {
            status: 500,
            data: { message: '500 Unknown Service Error.', err_code: 'test' },
        },
    };
    const error = errorResponse as AxiosError;

    expect(errorToParams(error)).toBe('?errorCode=test');
});
