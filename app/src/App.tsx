import React from 'react';
import './styles/App.scss';
import UploadDocumentsPage from './pages/uploadDocumentsPage/UploadDocumentsPage';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/homePage/HomePage';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import config from './config';
import { routes } from './types/generic/routes';
import PatientSearchPage from './pages/patientSearchPage/PatientSearchPage';
import OrgSelectPage from './pages/orgSelectPage/OrgSelectPage';
import Layout from './components/layout/serviceErrorBox/ServiceErrorBox';

function App() {
  return (
    <ConfigProvider config={config}>
      <Router>
        <Layout>
          <Routes>
            <Route element={<HomePage />} path={routes.HOME} />
            <Route element={<OrgSelectPage />} path={routes.SELECT_ORG} />
            <Route
              element={<PatientSearchPage route={routes.UPLOAD_SEARCH} />}
              path={routes.UPLOAD_SEARCH}
            />
            <Route
              element={<PatientSearchPage route={routes.DOWNLOAD_SEARCH} />}
              path={routes.DOWNLOAD_SEARCH}
            />
            <Route
              element={<UploadDocumentsPage />}
              path={routes.UPLOAD_DOCUMENTS}
            />
          </Routes>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}

export default App;
