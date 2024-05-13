import { REPOSITORY_ROLE } from './authRole';

export enum routes {
    START = '/',
    HOME = '/home',
    AUTH_CALLBACK = '/auth-callback',
    NOT_FOUND = '/*',
    UNAUTHORISED = '/unauthorised',
    AUTH_ERROR = '/auth-error',
    UNAUTHORISED_LOGIN = '/unauthorised-login',
    SERVER_ERROR = '/server-error',
    SESSION_EXPIRED = '/session-expired',
    PRIVACY_POLICY = '/privacy-policy',
    LOGOUT = '/logout',
    FEEDBACK = '/feedback',
    SEARCH_PATIENT = '/patient/search',
    VERIFY_PATIENT = '/patient/verify',
    LLOYD_GEORGE = '/patient/lloyd-george-record/',
    LLOYD_GEORGE_WILDCARD = '/patient/lloyd-george-record/*',
    LLOYD_GEORGE_UPLOAD = '/patient/lloyd-george-record/upload',
    LLOYD_GEORGE_UPLOAD_WILDCARD = '/patient/lloyd-george-record/upload/*',
    DOWNLOAD_DOCUMENTS = '/patient/download',
    ARF_UPLOAD_DOCUMENTS = '/patient/upload',
}

export enum routeChildren {
    LLOYD_GEORGE_DOWNLOAD = '/patient/lloyd-george-record/download',
    LLOYD_GEORGE_DOWNLOAD_COMPLETE = '/patient/lloyd-george-record/download/complete',
    LLOYD_GEORGE_DELETE = '/patient/lloyd-george-record/delete',
    LLOYD_GEORGE_DELETE_COMPLETE = '/patient/lloyd-george-record/delete/complete',
    LLOYD_GEORGE_UPLOAD_UPLOADING = '/patient/lloyd-george-record/upload/uploading',
    LLOYD_GEORGE_UPLOAD_COMPLETED = '/patient/lloyd-george-record/upload/completed',
    LLOYD_GEORGE_UPLOAD_FAILED = '/patient/lloyd-george-record/upload/failed',
    LLOYD_GEORGE_UPLOAD_INFECTED = '/patient/lloyd-george-record/upload/infected',
    LLOYD_GEORGE_UPLOAD_RETRY = '/patient/lloyd-george-record/upload/retry',
    LLOYD_GEORGE_UPLOAD_CONFIRMATION = '/patient/lloyd-george-record/upload/confirmation',
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
    children?: React.ReactNode;
};
