import { ErrorResponse } from '../../types/generic/errorResponse';
import { AxiosError } from 'axios';
import { unixTimestamp } from './createTimestamp';

export const errorToParams = (error: AxiosError) => {
    const errorResponse = error.response?.data as ErrorResponse;
    const { err_code = '', interaction_id = unixTimestamp().toString() } = errorResponse;
    const params = JSON.stringify([err_code, interaction_id]);
    return '?encodedError=' + btoa(params);
};
