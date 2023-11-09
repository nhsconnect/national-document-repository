import React from 'react';
import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import { routes } from '../types/generic/routes';
import HomePage from '../pages/homePage/HomePage';
import NotFoundPage from '../pages/notFoundPage/NotFoundPage';
import UnauthorisedPage from '../pages/unauthorisedPage/UnauthorisedPage';
import AuthErrorPage from '../pages/authErrorPage/AuthErrorPage';
import AuthCallbackPage from '../pages/authCallbackPage/AuthCallbackPage';
import AuthGuard from './guards/authGuard/AuthGuard';
import PatientSearchPage from '../pages/patientSearchPage/PatientSearchPage';
import LogoutPage from '../pages/logoutPage/LogoutPage';
import PatientGuard from './guards/patientGuard/PatientGuard';
import PatientResultPage from '../pages/patientResultPage/PatientResultPage';
import LloydGeorgeRecordPage from '../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import UploadDocumentsPage from '../pages/uploadDocumentsPage/UploadDocumentsPage';
import DocumentSearchResultsPage from '../pages/documentSearchResultsPage/DocumentSearchResultsPage';
import RoleGuard from './guards/roleGuard/RoleGuard';

const reactRouterToArray = require('react-router-to-array');

const AppRoutes = () => (
    <Routes>
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
                    <RoleGuard>
                        <PatientGuard>
                            <Outlet />
                        </PatientGuard>
                    </RoleGuard>
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
    </Routes>
);
const AppRouter = () => {
    return (
        <Router>
            <Layout>
                <AppRoutes />
            </Layout>
        </Router>
    );
};

export const sitemap = reactRouterToArray(AppRoutes);

export default AppRouter;
