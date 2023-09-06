import { AxiosError } from 'axios';

export type ErrorResponse = {
    response?: {
        status: number;
        message: string;
    } & AxiosError;
};
