import React from 'react';
import './styles/App.scss';
import HomePage from './pages/homePage/HomePage';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import config from './config';
import { routes } from './types/generic/routes';
import Layout from './components/layout/Layout';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import { BrowserRouter as Router, Route, Routes, Outlet } from 'react-router-dom';
import RoleSelectPage from './pages/roleSelectPage/RoleSelectPage';
import SessionProvider from './providers/sessionProvider/SessionProvider';
import AuthCallbackPage from './pages/authCallbackPage/AuthCallbackPage';
import NotFoundPage from './pages/notFoundPage/NotFoundPage';
import UnauthorisedPage from './pages/unauthorisedPage/UnauthorisedPage';
import AuthGuard from './components/blocks/authGuard/AuthGuard';
import { USER_ROLE } from './types/generic/roles';
import PatientSearchPage from './pages/patientSearchPage/PatientSearchPage';
import LogoutPage from './pages/logoutPage/LogoutPage';
import PatientGuard from './components/blocks/patientGuard/PatientGuard';
import PatientResultPage from './pages/patientResultPage/PatientResultPage';
import UploadDocumentsPage from './pages/uploadDocumentsPage/UploadDocumentsPage';
import DocumentSearchResultsPage from './pages/documentSearchResultsPage/DocumentSearchResultsPage';
import LloydGeorgeRecordPage from './pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';

function App() {
    return (
        <ConfigProvider config={config}>
            <SessionProvider>
                <PatientDetailsProvider>
                    <Router>
                        <Layout>
                            <Routes>
                                <Route element={<HomePage />} path={routes.HOME} />

                                <Route element={<NotFoundPage />} path={routes.NOT_FOUND} />
                                <Route element={<UnauthorisedPage />} path={routes.UNAUTHORISED} />
                                <Route element={<AuthCallbackPage />} path={routes.AUTH_CALLBACK} />
                                <Route element={<RoleSelectPage />} path={routes.SELECT_ORG} />

                                <Route
                                    element={
                                        <AuthGuard>
                                            <Outlet />
                                        </AuthGuard>
                                    }
                                >
                                    <Route
                                        element={<PatientSearchPage role={USER_ROLE.PCSE} />}
                                        path={routes.DOWNLOAD_SEARCH}
                                    />
                                    <Route
                                        element={<PatientSearchPage role={USER_ROLE.GP} />}
                                        path={routes.UPLOAD_SEARCH}
                                    />

                                    <Route element={<LogoutPage />} path={routes.LOGOUT} />
                                    <Route
                                        element={
                                            <PatientGuard>
                                                <Outlet />
                                            </PatientGuard>
                                        }
                                    >
                                        <Route
                                            element={<PatientResultPage role={USER_ROLE.PCSE} />}
                                            path={routes.DOWNLOAD_VERIFY}
                                        />
                                        <Route
                                            element={<PatientResultPage role={USER_ROLE.GP} />}
                                            path={routes.UPLOAD_VERIFY}
                                        />
                                        <Route
                                            element={<LloydGeorgeRecordPage />}
                                            path={routes.LLOYD_GEORGE}
                                        />
                                        <Route
                                            element={<UploadDocumentsPage />}
                                            path={routes.UPLOAD_DOCUMENTS}
                                        />
                                        <Route
                                            element={<DocumentSearchResultsPage />}
                                            path={routes.DOWNLOAD_DOCUMENTS}
                                        />
                                    </Route>
                                </Route>
                            </Routes>
                        </Layout>
                    </Router>
                </PatientDetailsProvider>
            </SessionProvider>
        </ConfigProvider>
    );
}

export default App;
