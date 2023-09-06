import React from 'react';
import type { ReactNode } from 'react';
import './styles/App.scss';
import HomePage from './pages/homePage/HomePage';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import config from './config';
import { routes } from './types/generic/routes';
import PatientResultPage from './pages/patientResultPage/PatientResultPage';
import Layout from './components/layout/Layout';
import { USER_ROLE } from './types/generic/roles';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import { BrowserRouter as Router, Route, Routes, Outlet } from 'react-router-dom';
import RoleSelectPage from './pages/roleSelectPage/RoleSelectPage';
import PatientSearchPage from './pages/patientSearchPage/PatientSearchPage';
import UploadDocumentsPage from './pages/uploadDocumentsPage/UploadDocumentsPage';

function App() {
    const AuthenticatedProviders = ({ children }: { children: ReactNode }) => (
        <PatientDetailsProvider>{children}</PatientDetailsProvider>
    );

    const AppProviders = ({ children }: { children: ReactNode }) => (
        <ConfigProvider config={config}>{children}</ConfigProvider>
    );

    return (
        <AppProviders>
            <Router>
                <Layout>
                    <Routes>
                        <Route element={<HomePage />} path={routes.HOME} />
                        <Route element={<RoleSelectPage />} path={routes.SELECT_ORG} />
                        <Route
                            element={
                                <AuthenticatedProviders>
                                    <Outlet />
                                </AuthenticatedProviders>
                            }
                        >
                            <Route
                                element={<PatientSearchPage role={USER_ROLE.PCSE} />}
                                path={routes.UPLOAD_SEARCH}
                            />
                            <Route
                                element={<PatientSearchPage role={USER_ROLE.GP} />}
                                path={routes.DOWNLOAD_SEARCH}
                            />
                            <Route
                                element={<PatientResultPage role={USER_ROLE.PCSE} />}
                                path={routes.DOWNLOAD_VERIFY}
                            />
                            <Route
                                element={<PatientResultPage role={USER_ROLE.GP} />}
                                path={routes.UPLOAD_VERIFY}
                            />
                            <Route
                                element={<UploadDocumentsPage />}
                                path={routes.UPLOAD_DOCUMENTS}
                            />
                        </Route>
                    </Routes>
                </Layout>
            </Router>
        </AppProviders>
    );
}

export default App;
