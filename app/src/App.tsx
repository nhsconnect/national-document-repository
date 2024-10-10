import React from 'react';
import './styles/App.scss';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/AppRouter';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import AxiosProvider from './providers/axiosProvider/AxiosProvider';

function App() {
    return (
        <ConfigProvider>
            <SessionProvider>
                <AxiosProvider>
                    <PatientDetailsProvider>
                        <AppRouter />
                    </PatientDetailsProvider>
                </AxiosProvider>
            </SessionProvider>
        </ConfigProvider>
    );
}

export default App;
