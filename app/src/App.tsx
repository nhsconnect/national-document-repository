import React from 'react';
import './styles/App.scss';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/AppRouter';

function App() {
    return (
        <SessionProvider>
            <PatientDetailsProvider>
                <AppRouter />
            </PatientDetailsProvider>
        </SessionProvider>
    );
}

export default App;
