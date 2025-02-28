import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';
import { AwsRum, AwsRumConfig } from 'aws-rum-web';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

if (process.env.REACT_APP_ENVIRONMENT === 'development') {
    try {
        const config: AwsRumConfig = {
            sessionSampleRate: 1,
            identityPoolId: process.env.REACT_APP_RUM_IDENTITY_POOL_ID || '',
            endpoint: `https://dataplane.rum.${
                process.env.REACT_APP_AWS_REGION || 'eu-west-2'
            }.amazonaws.com`,
            telemetries: ['http', 'errors', 'performance'],
            allowCookies: true,
            enableXRay: true,
        };

        const APPLICATION_ID: string = process.env.REACT_APP_MONITOR_ACCOUNT_ID || '';
        const APPLICATION_VERSION: string = '1.0.0';
        const APPLICATION_REGION: string = process.env.REACT_APP_AWS_REGION || 'eu-west-2';

        const awsRum: AwsRum = new AwsRum(
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
}

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
);
