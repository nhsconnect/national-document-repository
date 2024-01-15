import { REPOSITORY_ROLE } from './authRole';

export enum routes {
    START = '/',
    HOME = '/home',
    AUTH_CALLBACK = '/auth-callback',
    NOT_FOUND = '/*',
    UNAUTHORISED = '/unauthorised',
    AUTH_ERROR = '/auth-error',
    LOGOUT = '/logout',
    SEARCH_PATIENT = '/search/patient',
    VERIFY_PATIENT = '/search/patient/verify',
    LLOYD_GEORGE = '/patient/view/lloyd-george-record',
    DOWNLOAD_DOCUMENTS = '/patient/download',
    UPLOAD_DOCUMENTS = '/patient/upload',
}

export enum ROUTE_TYPE {
    // No guard
    PUBLIC = 0,
    // Auth route guard
    PRIVATE = 1,
    // All route guards
    PATIENT = 2,
}

export type route = {
    page: JSX.Element;
    type: ROUTE_TYPE;
    unauthorized?: Array<REPOSITORY_ROLE>;
};
