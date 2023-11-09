import React from 'react';
import './styles/App.scss';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import config from './config';
import Layout from './components/layout/Layout';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/Router';

function App() {
    return (
        <ConfigProvider config={config}>
            <SessionProvider>
                <PatientDetailsProvider>
                    <Layout>
                        <AppRouter />
                    </Layout>
                </PatientDetailsProvider>
            </SessionProvider>
        </ConfigProvider>
    );
}

export default App;
