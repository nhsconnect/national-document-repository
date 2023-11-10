import React from 'react';
import './styles/App.scss';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import config from './config';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/AppRouter';

function App() {
    return (
        <ConfigProvider config={config}>
            <SessionProvider>
                <PatientDetailsProvider>
                    <AppRouter />
                </PatientDetailsProvider>
            </SessionProvider>
        </ConfigProvider>
    );
}

export default App;
