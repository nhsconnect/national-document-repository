import { AxiosError } from 'axios';

export const isLocal =
    !import.meta.env.VITE_ENVIRONMENT || import.meta.env.VITE_ENVIRONMENT === 'local';

export const isMock = (err: AxiosError) => isLocal && err.code === 'ERR_NETWORK';

export const isRunningInCypress = () => {
    //@ts-ignore
    return Boolean(window?.Cypress) || typeof jest !== 'undefined';
};
