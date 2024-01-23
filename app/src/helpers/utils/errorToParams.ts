import { ErrorResponse } from '../../types/generic/errorResponse';
import { AxiosError } from 'axios';

export const errorToParams = (error: AxiosError) => {
    const errorResponse = error.response?.data as ErrorResponse;
    return errorResponse.err_code ? '?errorCode=' + errorResponse.err_code : '';
};
