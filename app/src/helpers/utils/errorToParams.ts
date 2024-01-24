import { ErrorResponse } from '../../types/generic/errorResponse';
import { AxiosError } from 'axios';

export const errorToParams = (error: AxiosError) => {
    const errorResponse = error.response?.data as ErrorResponse;
    const { err_code, interaction_id } = errorResponse;
    const params = JSON.stringify([err_code, interaction_id]);
    return '?encodedError=' + btoa(params);
};
