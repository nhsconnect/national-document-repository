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
    SEARCH_PATIENT = '/search/patient',
    VERIFY_PATIENT = '/search/patient/verify',
    LLOYD_GEORGE = '/patient/view/lloyd-george-record',
    LLOYD_GEORGE_UPLOAD = '/patient/upload/lloyd-george-record',
    LLOYD_GEORGE_UPLOAD_WILDCARD = '/patient/upload/lloyd-george-record/*',
    ARF_DOWNLOAD_DOCUMENTS = '/patient/download',
    ARF_UPLOAD_DOCUMENTS = '/patient/upload',
}

export enum routeChildren {
    LLOYD_GEORGE_UPLOAD_SELECTION = '/patient/upload/lloyd-george-record/selection',
    LLOYD_GEORGE_UPLOAD_UPLOAD = '/patient/upload/lloyd-george-record/upload',
    LLOYD_GEORGE_UPLOAD_COMPLETED = '/patient/upload/lloyd-george-record/completed',
    LLOYD_GEORGE_UPLOAD_FAILED = '/patient/upload/lloyd-george-record/failed',
    LLOYD_GEORGE_UPLOAD_INFECTED = '/patient/upload/lloyd-george-record/infected',
    LLOYD_GEORGE_UPLOAD_CONFIRMATION = '/patient/upload/lloyd-george-record/confirmation',
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
