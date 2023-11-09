import { REPOSITORY_ROLE } from './authRole';

export enum routes {
    HOME = '/',
    AUTH_CALLBACK = '/auth-callback',
    NOT_FOUND = '/*',
    UNAUTHORISED = '/unauthorised',
    AUTH_ERROR = '/auth-error',

    LOGOUT = '/logout',

    DOWNLOAD_SEARCH = '/search/patient',
    DOWNLOAD_VERIFY = '/search/patient/result',
    DOWNLOAD_DOCUMENTS = '/search/results',

    LLOYD_GEORGE = '/search/patient/lloyd-george-record',

    UPLOAD_SEARCH = '/search/upload',
    UPLOAD_VERIFY = '/search/upload/result',
    UPLOAD_DOCUMENTS = '/upload/submit',
}

export enum ROUTE_GUARD {
    AUTH = 0,
    ROLE = 1,
    PATIENT = 2,
}

export type route = {
    page: JSX.Element;
    guards?: Array<ROUTE_GUARD>;
    unauthorized?: Array<REPOSITORY_ROLE>;
};
