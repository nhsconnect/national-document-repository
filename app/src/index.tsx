import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/index.css';
import App from './App';
import { AwsRum } from 'aws-rum-web';

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

if (process.env.REACT_APP_ENVIRONMENT === 'development') {
    new AwsRum(
        process.env.REACT_APP_RUM_APP_ID || '',
        process.env.REACT_APP_AWS_REGION || 'eu-west-2',
        '1.0.0',
        {
            sessionSampleRate: 1.0, // Capture all sessions
            guestRoleArn: `arn:aws:iam::${process.env.REACT_APP_AWS_ACCOUNT_ID}:role/RumServiceRole`,
            identityPoolId: process.env.REACT_APP_RUM_IDENTITY_POOL_ID || '',
            endpoint: `https://dataplane.rum.${
                process.env.REACT_APP_AWS_REGION || 'eu-west-2'
            }.amazonaws.com`,
            telemetries: ['performance', 'errors', 'http'],
            allowCookies: true,
            enableXRay: true,
        },
    );
}

root.render(
    <React.StrictMode>
        <App />
    </React.StrictMode>,
);
