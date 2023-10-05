export enum routes {
    HOME = '/',
    SELECT_ORG = '/select-organisation',
    AUTH_CALLBACK = '/auth-callback',
    NOT_FOUND = '/*',
    UNAUTHORISED = '/unauthorised',
    LOGOUT = '/logout',

    DOWNLOAD_SEARCH = '/search/patient',
    DOWNLOAD_VERIFY = '/search/patient/result',
    DOWNLOAD_DOCUMENTS = '/search/results',
    DELETE_DOCUMENTS = '/search/results/delete',

    LLOYD_GEORGE = '/lloyd-george-record',

    UPLOAD_SEARCH = '/search/upload',
    UPLOAD_VERIFY = '/search/upload/result',
    UPLOAD_DOCUMENTS = '/upload/submit',
}
