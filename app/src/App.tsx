import React from 'react';
import './styles/App.scss';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/AppRouter';
import FeatureFlagsProvider from './providers/featureFlagsProvider/FeatureFlagsProvider';

function App() {
    return (
        <SessionProvider>
            <FeatureFlagsProvider>
                <PatientDetailsProvider>
                    <AppRouter />
                </PatientDetailsProvider>
            </FeatureFlagsProvider>
        </SessionProvider>
    );
}

export default App;
