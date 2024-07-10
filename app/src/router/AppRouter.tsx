import React from 'react';
import { BrowserRouter as Router, Outlet, Route, Routes as Switch } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { route, ROUTE_TYPE, routeChildren, routes } from '../types/generic/routes';
import StartPage from '../pages/startPage/StartPage';
import AuthCallbackPage from '../pages/authCallbackPage/AuthCallbackPage';
import NotFoundPage from '../pages/notFoundPage/NotFoundPage';
import AuthErrorPage from '../pages/authErrorPage/AuthErrorPage';
import UnauthorisedPage from '../pages/unauthorisedPage/UnauthorisedPage';
import LogoutPage from '../pages/logoutPage/LogoutPage';
import PatientSearchPage from '../pages/patientSearchPage/PatientSearchPage';
import PatientResultPage from '../pages/patientResultPage/PatientResultPage';
import ArfUploadDocumentsPage from '../pages/uploadDocumentsPage/UploadDocumentsPage';
import ArfSearchResultsPage from '../pages/documentSearchResultsPage/DocumentSearchResultsPage';
import LloydGeorgeRecordPage from '../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import AuthGuard from './guards/authGuard/AuthGuard';
import PatientGuard from './guards/patientGuard/PatientGuard';
import { REPOSITORY_ROLE } from '../types/generic/authRole';
import RoleGuard from './guards/roleGuard/RoleGuard';
import HomePage from '../pages/homePage/HomePage';
import UnauthorisedLoginPage from '../pages/unauthorisedLoginPage/UnauthorisedLoginPage';
import FeedbackPage from '../pages/feedbackPage/FeedbackPage';
import ServerErrorPage from '../pages/serverErrorPage/ServerErrorPage';
import PrivacyPage from '../pages/privacyPage/PrivacyPage';
import LloydGeorgeUploadPage from '../pages/lloydGeorgeUploadPage/LloydGeorgeUploadPage';
import SessionExpiredErrorPage from '../pages/sessionExpiredErrorPage/SessionExpiredErrorPage';
import FeedbackConfirmationPage from '../pages/feedbackConfirmationPage/FeedbackConfirmationPage';

const {
    START,
    HOME,
    AUTH_CALLBACK,
    NOT_FOUND,
    UNAUTHORISED,
    UNAUTHORISED_LOGIN,
    AUTH_ERROR,
    SERVER_ERROR,
    SESSION_EXPIRED,
    FEEDBACK,
    FEEDBACK_CONFIRMATION,
    LOGOUT,
    SEARCH_PATIENT,
    VERIFY_PATIENT,
    PRIVACY_POLICY,
    LLOYD_GEORGE,
    LLOYD_GEORGE_WILDCARD,
    LLOYD_GEORGE_UPLOAD,
    LLOYD_GEORGE_UPLOAD_WILDCARD,
    ARF_OVERVIEW,
    ARF_OVERVIEW_WILDCARD,
    ARF_UPLOAD_DOCUMENTS,
    ARF_UPLOAD_DOCUMENTS_WILDCARD,
} = routes;

type Routes = {
    [key in routes]: route;
};

export const childRoutes = [
    {
        route: routeChildren.LLOYD_GEORGE_DOWNLOAD,
        parent: LLOYD_GEORGE,
    },
    {
        route: routeChildren.LLOYD_GEORGE_DOWNLOAD_SELECT,
        parent: LLOYD_GEORGE,
    },
    {
        route: routeChildren.LLOYD_GEORGE_DOWNLOAD_COMPLETE,
        parent: LLOYD_GEORGE,
    },
    {
        route: routeChildren.LLOYD_GEORGE_DOWNLOAD_IN_PROGRESS,
        parent: LLOYD_GEORGE,
    },
    {
        route: routeChildren.LLOYD_GEORGE_DELETE,
        parent: LLOYD_GEORGE,
    },
    {
        route: routeChildren.LLOYD_GEORGE_DELETE_CONFIRMATION,
        parent: LLOYD_GEORGE,
    },
    {
        route: routeChildren.LLOYD_GEORGE_DELETE_COMPLETE,
        parent: LLOYD_GEORGE,
    },
    {
        route: routeChildren.LLOYD_GEORGE_UPLOAD_UPLOADING,
        parent: LLOYD_GEORGE_UPLOAD,
    },
    {
        route: routeChildren.LLOYD_GEORGE_UPLOAD_COMPLETED,
        parent: LLOYD_GEORGE_UPLOAD,
    },
    {
        route: routeChildren.LLOYD_GEORGE_UPLOAD_CONFIRMATION,
        parent: LLOYD_GEORGE_UPLOAD,
    },
    {
        route: routeChildren.LLOYD_GEORGE_UPLOAD_INFECTED,
        parent: LLOYD_GEORGE_UPLOAD,
    },
    {
        route: routeChildren.LLOYD_GEORGE_UPLOAD_FAILED,
        parent: LLOYD_GEORGE_UPLOAD,
    },
    {
        route: routeChildren.LLOYD_GEORGE_UPLOAD_RETRY,
        parent: LLOYD_GEORGE_UPLOAD,
    },
    {
        route: routeChildren.ARF_DELETE,
        parent: ARF_OVERVIEW,
    },
    {
        route: routeChildren.ARF_DELETE_CONFIRMATION,
        parent: ARF_OVERVIEW,
    },
    {
        route: routeChildren.ARF_DELETE_COMPLETE,
        parent: ARF_OVERVIEW,
    },
    {
        route: routeChildren.ARF_UPLOAD_UPLOADING,
        parent: ARF_UPLOAD_DOCUMENTS,
    },
    {
        route: routeChildren.ARF_UPLOAD_COMPLETED,
        parent: ARF_UPLOAD_DOCUMENTS,
    },
    {
        route: routeChildren.ARF_UPLOAD_FAILED,
        parent: ARF_UPLOAD_DOCUMENTS,
    },
    {
        route: routeChildren.ARF_UPLOAD_CONFIRMATION,
        parent: ARF_UPLOAD_DOCUMENTS,
    },
    {
        route: routeChildren.ARF_UPLOAD_CONFIRMATION_FAILED,
        parent: ARF_UPLOAD_DOCUMENTS,
    },
];

export const routeMap: Routes = {
    // Public routes
    [START]: {
        page: <StartPage />,
        type: ROUTE_TYPE.PUBLIC,
    },
    [AUTH_CALLBACK]: {
        page: <AuthCallbackPage />,
        type: ROUTE_TYPE.PUBLIC,
    },
    [NOT_FOUND]: {
        page: <NotFoundPage />,
        type: ROUTE_TYPE.PUBLIC,
    },
    [AUTH_ERROR]: {
        page: <AuthErrorPage />,
        type: ROUTE_TYPE.PUBLIC,
    },
    [UNAUTHORISED]: {
        page: <UnauthorisedPage />,
        type: ROUTE_TYPE.PUBLIC,
    },
    [UNAUTHORISED_LOGIN]: {
        page: <UnauthorisedLoginPage />,
        type: ROUTE_TYPE.PUBLIC,
    },
    [SERVER_ERROR]: {
        page: <ServerErrorPage />,
        type: ROUTE_TYPE.PUBLIC,
    },
    [SESSION_EXPIRED]: {
        page: <SessionExpiredErrorPage />,
        type: ROUTE_TYPE.PUBLIC,
    },
    [PRIVACY_POLICY]: {
        page: <PrivacyPage />,
        type: ROUTE_TYPE.PUBLIC,
    },

    // Auth guard routes
    [LOGOUT]: {
        page: <LogoutPage />,
        type: ROUTE_TYPE.PRIVATE,
    },
    [HOME]: {
        page: <HomePage />,
        type: ROUTE_TYPE.PRIVATE,
    },
    [SEARCH_PATIENT]: {
        page: <PatientSearchPage />,
        type: ROUTE_TYPE.PRIVATE,
    },
    [FEEDBACK]: {
        page: <FeedbackPage />,
        type: ROUTE_TYPE.PRIVATE,
    },
    [FEEDBACK_CONFIRMATION]: {
        page: <FeedbackConfirmationPage />,
        type: ROUTE_TYPE.PRIVATE,
    },
    // App guard routes
    [VERIFY_PATIENT]: {
        page: <PatientResultPage />,
        type: ROUTE_TYPE.PATIENT,
    },
    [LLOYD_GEORGE]: {
        page: <LloydGeorgeRecordPage />,
        type: ROUTE_TYPE.PATIENT,
        unauthorized: [REPOSITORY_ROLE.PCSE],
    },
    [LLOYD_GEORGE_WILDCARD]: {
        page: <LloydGeorgeRecordPage />,
        type: ROUTE_TYPE.PATIENT,
        unauthorized: [REPOSITORY_ROLE.PCSE],
    },
    [LLOYD_GEORGE_UPLOAD]: {
        page: <LloydGeorgeUploadPage />,
        type: ROUTE_TYPE.PATIENT,
        unauthorized: [REPOSITORY_ROLE.PCSE],
    },
    [LLOYD_GEORGE_UPLOAD_WILDCARD]: {
        page: <LloydGeorgeUploadPage />,
        type: ROUTE_TYPE.PATIENT,
        unauthorized: [REPOSITORY_ROLE.PCSE],
    },
    [ARF_OVERVIEW]: {
        page: <ArfSearchResultsPage />,
        type: ROUTE_TYPE.PATIENT,
        unauthorized: [REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL],
    },
    [ARF_OVERVIEW_WILDCARD]: {
        page: <ArfSearchResultsPage />,
        type: ROUTE_TYPE.PATIENT,
        unauthorized: [REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL],
    },
    [ARF_UPLOAD_DOCUMENTS]: {
        page: <ArfUploadDocumentsPage />,
        type: ROUTE_TYPE.PATIENT,
        unauthorized: [REPOSITORY_ROLE.PCSE],
    },
    [ARF_UPLOAD_DOCUMENTS_WILDCARD]: {
        page: <ArfUploadDocumentsPage />,
        type: ROUTE_TYPE.PATIENT,
        unauthorized: [REPOSITORY_ROLE.PCSE],
    },
};

const createRoutesFromType = (routeType: ROUTE_TYPE) =>
    Object.entries(routeMap).reduce(
        (acc, [path, route]) =>
            route.type === routeType
                ? [...acc, <Route key={path} path={path} element={route.page} />]
                : acc,
        [] as Array<JSX.Element>,
    );

const AppRoutes = () => {
    const publicRoutes = createRoutesFromType(ROUTE_TYPE.PUBLIC);
    const privateRoutes = createRoutesFromType(ROUTE_TYPE.PRIVATE);
    const patientRoutes = createRoutesFromType(ROUTE_TYPE.PATIENT);

    return (
        <Switch>
            {publicRoutes}
            <Route
                element={
                    <RoleGuard>
                        <AuthGuard>
                            <Outlet />
                        </AuthGuard>
                    </RoleGuard>
                }
            >
                {privateRoutes}
                <Route
                    element={
                        <PatientGuard>
                            <Outlet />
                        </PatientGuard>
                    }
                >
                    {patientRoutes}
                </Route>
            </Route>
        </Switch>
    );
};

const AppRouter = () => {
    return (
        <Router>
            <Layout>
                <AppRoutes />
            </Layout>
        </Router>
    );
};

export default AppRouter;
