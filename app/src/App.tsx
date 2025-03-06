import React, { useEffect, useRef } from 'react';
import './styles/App.scss';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider, { useSessionContext } from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/AppRouter';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import { AwsRum, AwsRumConfig } from 'aws-rum-web';
let awsRumInstance: AwsRum | null = null;

function App() {
    const [session] = useSessionContext();
    const roleRef = useRef<string | null>(null);

    useEffect(() => {
        // Initialize AWS RUM immediately when App mounts
        if (process.env.REACT_APP_ENVIRONMENT === 'development' && !awsRumInstance) {
            try {
                const config: AwsRumConfig = {
                    sessionSampleRate: 1,
                    identityPoolId: process.env.REACT_APP_RUM_IDENTITY_POOL_ID || '',
                    endpoint: `https://dataplane.rum.eu-west-2.amazonaws.com`,
                    telemetries: ['http', 'errors', 'performance'],
                    allowCookies: true,
                    enableXRay: false,
                };

                const APPLICATION_ID: string = process.env.REACT_APP_MONITOR_ACCOUNT_ID || '';
                const APPLICATION_VERSION: string = '1.0.0';
                const APPLICATION_REGION: string = process.env.REACT_APP_AWS_REGION || 'eu-west-2';

                awsRumInstance = new AwsRum(
                    APPLICATION_ID,
                    APPLICATION_VERSION,
                    APPLICATION_REGION,
                    config,
                );

                console.log('AWS RUM Initialized Successfully'); // eslint-disable-line
            } catch (error) {
                console.log('AWS RUM Initialization Failed:', error); // eslint-disable-line
            }
        }

        // Add user role to RUM session attributes if available
        if (awsRumInstance && session?.auth?.role && session.auth.role !== roleRef.current) {
            awsRumInstance.addSessionAttributes({
                userRole: session.auth.role,
            });
            roleRef.current = session.auth.role;
            console.log('User role added to AWS RUM:', session.auth.role); // eslint-disable-line
        }
    }, [session]);
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
