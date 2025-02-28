import React from 'react';
import './styles/App.scss';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/AppRouter';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import { AwsRum, AwsRumConfig } from 'aws-rum-web';

if (process.env.REACT_APP_ENVIRONMENT === 'development') {
    try {
        const config: AwsRumConfig = {
            sessionSampleRate: 1,
            identityPoolId:
                process.env.REACT_APP_RUM_IDENTITY_POOL_ID ||
                'eu-west-2:5d286c6d-f8bd-49eb-930a-eb650a56427c',
            endpoint: `https://dataplane.rum.eu-west-2.amazonaws.com`,
            telemetries: ['http', 'errors', 'performance'],
            allowCookies: true,
            enableXRay: true,
        };

        const APPLICATION_ID: string =
            process.env.REACT_APP_MONITOR_ACCOUNT_ID || '45c1bd72-49c2-4d95-b25c-7f8f28e62153';
        const APPLICATION_VERSION: string = '1.0.0';
        const APPLICATION_REGION: string = process.env.REACT_APP_AWS_REGION || 'eu-west-2';

        const awsRum: AwsRum = new AwsRum( // eslint-disable-line
            APPLICATION_ID,
            APPLICATION_VERSION,
            APPLICATION_REGION,
            config,
        ); // eslint-disable-line
        // eslint-disable-next-line no-console
        console.log('RUM client initialized');
    } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error);
    }
} else {
    // eslint-disable-next-line no-console
    console.log('RUM client not initialized');
}

function App() {
    return (
        <ConfigProvider>
            <SessionProvider>
                <PatientDetailsProvider>
                    <AppRouter />
                </PatientDetailsProvider>
            </SessionProvider>
        </ConfigProvider>
    );
}
export default App;
