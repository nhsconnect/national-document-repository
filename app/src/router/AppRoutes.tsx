import AuthCallbackPage from '../pages/authCallbackPage/AuthCallbackPage';
import AuthErrorPage from '../pages/authErrorPage/AuthErrorPage';
import DocumentSearchResultsPage from '../pages/documentSearchResultsPage/DocumentSearchResultsPage';
import HomePage from '../pages/homePage/HomePage';
import LloydGeorgeRecordPage from '../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import LogoutPage from '../pages/logoutPage/LogoutPage';
import NotFoundPage from '../pages/notFoundPage/NotFoundPage';
import PatientResultPage from '../pages/patientResultPage/PatientResultPage';
import PatientSearchPage from '../pages/patientSearchPage/PatientSearchPage';
import UnauthorisedPage from '../pages/unauthorisedPage/UnauthorisedPage';
import UploadDocumentsPage from '../pages/uploadDocumentsPage/UploadDocumentsPage';
import { ROUTE_GUARD, routes, route } from '../types/generic/routes';
const {
    HOME,
    AUTH_CALLBACK,
    NOT_FOUND,
    UNAUTHORISED,
    AUTH_ERROR,
    LOGOUT,
    DOWNLOAD_SEARCH,
    DOWNLOAD_VERIFY,
    DOWNLOAD_DOCUMENTS,
    LLOYD_GEORGE,
    UPLOAD_SEARCH,
    UPLOAD_VERIFY,
    UPLOAD_DOCUMENTS,
} = routes;

type AppRoutes = {
    [key in routes]: route;
};

export const appRoutes: AppRoutes = {
    [HOME]: {
        page: <HomePage />,
    },
    [AUTH_CALLBACK]: {
        page: <AuthCallbackPage />,
    },
    [NOT_FOUND]: {
        page: <NotFoundPage />,
    },
    [AUTH_ERROR]: {
        page: <AuthErrorPage />,
    },
    [UNAUTHORISED]: {
        page: <UnauthorisedPage />,
    },
    [LOGOUT]: {
        page: <LogoutPage />,
        guards: [ROUTE_GUARD.AUTH],
    },

    [DOWNLOAD_SEARCH]: {
        page: <PatientSearchPage />,
        guards: [ROUTE_GUARD.AUTH, ROUTE_GUARD.ROLE],
    },
    [UPLOAD_SEARCH]: {
        page: <PatientSearchPage />,
        guards: [ROUTE_GUARD.AUTH, ROUTE_GUARD.ROLE],
    },
    [UPLOAD_VERIFY]: {
        page: <PatientResultPage />,
        guards: [ROUTE_GUARD.AUTH, ROUTE_GUARD.ROLE, ROUTE_GUARD.PATIENT],
    },
    [DOWNLOAD_VERIFY]: {
        page: <PatientResultPage />,
        guards: [ROUTE_GUARD.AUTH, ROUTE_GUARD.ROLE, ROUTE_GUARD.PATIENT],
    },

    [UPLOAD_DOCUMENTS]: {
        page: <UploadDocumentsPage />,
        guards: [ROUTE_GUARD.AUTH, ROUTE_GUARD.ROLE, ROUTE_GUARD.PATIENT],
    },
    [DOWNLOAD_DOCUMENTS]: {
        page: <DocumentSearchResultsPage />,
        guards: [ROUTE_GUARD.AUTH, ROUTE_GUARD.ROLE, ROUTE_GUARD.PATIENT],
    },
    [LLOYD_GEORGE]: {
        page: <LloydGeorgeRecordPage />,
        guards: [ROUTE_GUARD.AUTH, ROUTE_GUARD.ROLE, ROUTE_GUARD.PATIENT],
    },
};

export default appRoutes;
