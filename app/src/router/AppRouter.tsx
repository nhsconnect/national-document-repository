import React from 'react';
import { BrowserRouter as Router, Routes as Switch, Route, Outlet } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { ROUTE_TYPE, route, routes } from '../types/generic/routes';
import HomePage from '../pages/homePage/HomePage';
import AuthCallbackPage from '../pages/authCallbackPage/AuthCallbackPage';
import NotFoundPage from '../pages/notFoundPage/NotFoundPage';
import AuthErrorPage from '../pages/authErrorPage/AuthErrorPage';
import UnauthorisedPage from '../pages/unauthorisedPage/UnauthorisedPage';
import LogoutPage from '../pages/logoutPage/LogoutPage';
import PatientSearchPage from '../pages/patientSearchPage/PatientSearchPage';
import PatientResultPage from '../pages/patientResultPage/PatientResultPage';
import UploadDocumentsPage from '../pages/uploadDocumentsPage/UploadDocumentsPage';
import DocumentSearchResultsPage from '../pages/documentSearchResultsPage/DocumentSearchResultsPage';
import LloydGeorgeRecordPage from '../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import AuthGuard from './guards/authGuard/AuthGuard';
import PatientGuard from './guards/patientGuard/PatientGuard';
import { REPOSITORY_ROLE } from '../types/generic/authRole';
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

type Routes = {
    [key in routes]: route;
};

export const routeMap: Routes = {
    // Public routes
    [HOME]: {
        page: <HomePage />,
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

    // Auth guard routes
    [LOGOUT]: {
        page: <LogoutPage />,
        type: ROUTE_TYPE.PRIVATE,
    },

    // App guard routes
    [DOWNLOAD_SEARCH]: {
        page: <PatientSearchPage />,
        type: ROUTE_TYPE.APP,
        unauthorized: [REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL],
    },
    [UPLOAD_SEARCH]: {
        page: <PatientSearchPage />,
        type: ROUTE_TYPE.APP,
        unauthorized: [REPOSITORY_ROLE.PCSE],
    },
    [DOWNLOAD_VERIFY]: {
        page: <PatientResultPage />,
        type: ROUTE_TYPE.APP,
        unauthorized: [REPOSITORY_ROLE.GP_ADMIN, REPOSITORY_ROLE.GP_CLINICAL],
    },
    [UPLOAD_VERIFY]: {
        page: <PatientResultPage />,
        type: ROUTE_TYPE.APP,
        unauthorized: [REPOSITORY_ROLE.PCSE],
    },
    [UPLOAD_DOCUMENTS]: {
        page: <UploadDocumentsPage />,
        type: ROUTE_TYPE.APP,
    },
    [DOWNLOAD_DOCUMENTS]: {
        page: <DocumentSearchResultsPage />,
        type: ROUTE_TYPE.APP,
    },
    [LLOYD_GEORGE]: {
        page: <LloydGeorgeRecordPage />,
        type: ROUTE_TYPE.APP,
    },
};

// const AppRoutes = () => {
//     let unusedPaths = Object.keys(routeMap);
//     const appRoutesArr = Object.entries(routeMap);
//     const publicRoutes = appRoutesArr.map(([path, route]) => {
//         if (!route.guards && unusedPaths.includes(path)) {
//             unusedPaths = unusedPaths.filter((p) => p !== path);
//             return <Route key={path} path={path} element={route.page} />;
//         }
//     });
//     const patientRoutes = appRoutesArr.map(([path, route]) => {
//         if (
//             route.guards &&
//             route.guards.includes(ROUTE_GUARD.PATIENT) &&
//             unusedPaths.includes(path)
//         ) {
//             unusedPaths = unusedPaths.filter((p) => p !== path);
//             return <Route key={path} path={path} element={route.page} />;
//         }
//     });
//     const roleRoutes = appRoutesArr.map(([path, route]) => {
//         if (route.guards && route.guards.includes(ROUTE_GUARD.ROLE) && unusedPaths.includes(path)) {
//             unusedPaths = unusedPaths.filter((p) => p !== path);
//             return <Route key={path} path={path} element={route.page} />;
//         }
//     });
//     const privateRoutes = appRoutesArr.map(([path, route]) => {
//         if (route.guards && route.guards.includes(ROUTE_GUARD.AUTH) && unusedPaths.includes(path)) {
//             unusedPaths = unusedPaths.filter((p) => p !== path);
//             return <Route key={path} path={path} element={route.page} />;
//         }
//     });
//     return (
//         <Switch>
//             {publicRoutes}
//             <Route
//                 element={
//                     <AuthGuard>
//                         <Outlet />
//                     </AuthGuard>
//                 }
//             >
//                 {privateRoutes}
//                 <Route
//                     element={
//                         <RoleGuard>
//                             <PatientGuard>
//                                 <Outlet />
//                             </PatientGuard>
//                         </RoleGuard>
//                     }
//                 >
//                     {roleRoutes}
//                     {patientRoutes}
//                 </Route>
//             </Route>
//         </Switch>
//     );
// };

const PrevRoutes = () => (
    <Switch>
        <Route element={<HomePage />} path={routes.HOME} />

        <Route element={<NotFoundPage />} path={routes.NOT_FOUND} />
        <Route element={<UnauthorisedPage />} path={routes.UNAUTHORISED} />
        <Route element={<AuthErrorPage />} path={routes.AUTH_ERROR} />

        <Route element={<AuthCallbackPage />} path={routes.AUTH_CALLBACK} />

        <Route
            element={
                <AuthGuard>
                    <Outlet />
                </AuthGuard>
            }
        >
            {[routes.DOWNLOAD_SEARCH, routes.UPLOAD_SEARCH].map((searchRoute) => (
                <Route key={searchRoute} element={<PatientSearchPage />} path={searchRoute} />
            ))}

            <Route element={<LogoutPage />} path={routes.LOGOUT} />
            <Route
                element={
                    <PatientGuard>
                        <Outlet />
                    </PatientGuard>
                }
            >
                {[routes.DOWNLOAD_VERIFY, routes.UPLOAD_VERIFY].map((searchResultRoute) => (
                    <Route
                        key={searchResultRoute}
                        element={<PatientResultPage />}
                        path={searchResultRoute}
                    />
                ))}
                <Route element={<LloydGeorgeRecordPage />} path={routes.LLOYD_GEORGE} />
                <Route element={<UploadDocumentsPage />} path={routes.UPLOAD_DOCUMENTS} />
                <Route element={<DocumentSearchResultsPage />} path={routes.DOWNLOAD_DOCUMENTS} />
            </Route>
        </Route>
    </Switch>
);

const AppRouter = () => {
    return (
        <Router>
            <Layout>
                <PrevRoutes />
            </Layout>
        </Router>
    );
};

export default AppRouter;
