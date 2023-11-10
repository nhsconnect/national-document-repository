import React from 'react';
import { BrowserRouter as Router, Routes as Switch, Route, Outlet } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { ROUTE_GUARD, route, routes } from '../types/generic/routes';
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
import RoleGuard from './guards/roleGuard/RoleGuard';
import PatientGuard from './guards/patientGuard/PatientGuard';
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
    /**
     * Public routes
     */
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

    /**
     * Auth guarded routes
     */
    [LOGOUT]: {
        page: <LogoutPage />,
        guards: [ROUTE_GUARD.AUTH],
    },

    /**
     * Role guarded routes
     */
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

    /**
     * Patient guarded routes
     */
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

const AppRoutes = () => {
    let unusedPaths = Object.keys(routeMap);
    const appRoutesArr = Object.entries(routeMap);
    const publicRoutes = appRoutesArr.map(([path, route]) => {
        if (!route.guards && unusedPaths.includes(path)) {
            unusedPaths = unusedPaths.filter((p) => p !== path);
            return <Route key={path} path={path} element={route.page} />;
        }
    });
    const patientRoutes = appRoutesArr.map(([path, route]) => {
        if (
            route.guards &&
            route.guards.includes(ROUTE_GUARD.PATIENT) &&
            unusedPaths.includes(path)
        ) {
            unusedPaths = unusedPaths.filter((p) => p !== path);
            return <Route key={path} path={path} element={route.page} />;
        }
    });
    const roleRoutes = appRoutesArr.map(([path, route]) => {
        if (route.guards && route.guards.includes(ROUTE_GUARD.ROLE) && unusedPaths.includes(path)) {
            unusedPaths = unusedPaths.filter((p) => p !== path);
            return <Route key={path} path={path} element={route.page} />;
        }
    });
    const privateRoutes = appRoutesArr.map(([path, route]) => {
        if (route.guards && route.guards.includes(ROUTE_GUARD.AUTH) && unusedPaths.includes(path)) {
            unusedPaths = unusedPaths.filter((p) => p !== path);
            return <Route key={path} path={path} element={route.page} />;
        }
    });
    return (
        <Switch>
            {...publicRoutes}
            <Route
                element={
                    <AuthGuard>
                        <Outlet />
                    </AuthGuard>
                }
            >
                {...privateRoutes}
                <Route
                    element={
                        <RoleGuard>
                            <PatientGuard>
                                <Outlet />
                            </PatientGuard>
                        </RoleGuard>
                    }
                >
                    {...[...patientRoutes, ...roleRoutes]}
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
