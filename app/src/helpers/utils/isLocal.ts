import { AxiosError } from 'axios';

export const isLocal =
    !process.env.REACT_APP_ENVIRONMENT || process.env.REACT_APP_ENVIRONMENT === 'local';

export const isMock = (err: AxiosError) => isLocal && err.code === 'ERR_NETWORK';
