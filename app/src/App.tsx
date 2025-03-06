import './styles/App.scss';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider, { useSessionContext } from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/AppRouter';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import { AwsRum, AwsRumConfig } from 'aws-rum-web';

let awsRumInstance: AwsRum | null = null;

if (process.env.REACT_APP_ENVIRONMENT === 'development') {
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

        awsRumInstance = new AwsRum( // eslint-disable-line
            APPLICATION_ID,
            APPLICATION_VERSION,
            APPLICATION_REGION,
            config,
        );
    } catch (error) {
        console.log(error); // eslint-disable-line
    }
}

function App() {
    console.log(useSessionContext()); // eslint-disable-line

    const session = sessionStorage.getItem('UserSession');
    if (session != null) {
        const data = JSON.parse(session);
        console.log(data); // eslint-disable-line
        if (data.auth !== null && awsRumInstance !== null) {
            awsRumInstance.addSessionAttributes({
                userRole: data.auth.role,
            });
            console.log(data); // eslint-disable-line
        }
    }

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
