import './styles/App.scss';
import PatientDetailsProvider from './providers/patientProvider/PatientProvider';
import SessionProvider from './providers/sessionProvider/SessionProvider';
import AppRouter from './router/AppRouter';
import ConfigProvider from './providers/configProvider/ConfigProvider';
import { AwsRum, AwsRumConfig } from 'aws-rum-web';
import { NdrTokenData } from './types/generic/ndrTokenData';
import { decodeJwtToken } from './helpers/utils/jwtDecoder';

const cypress =
    process.env.REACT_APP_MONITOR_ACCOUNT_ID === 'not provided yet' &&
    process.env.REACT_APP_RUM_IDENTITY_POOL_ID === 'not provided yet';

if (process.env.REACT_APP_ENVIRONMENT === 'development' && !cypress) {
    try {
        const config: AwsRumConfig = {
            sessionSampleRate: 1,
            identityPoolId: process.env.REACT_APP_RUM_IDENTITY_POOL_ID || '',
            endpoint: `https://dataplane.rum.eu-west-2.amazonaws.com`,
            telemetries: ['http', 'errors', 'performance'],
            allowCookies: true,
            enableXRay: false,
        };
        const session = sessionStorage.getItem('UserSession');
        const APPLICATION_ID: string = process.env.REACT_APP_MONITOR_ACCOUNT_ID || '';
        const APPLICATION_VERSION: string = '1.0.0';
        const APPLICATION_REGION: string = process.env.REACT_APP_AWS_REGION || 'eu-west-2';

        const awsRum: AwsRum = new AwsRum( // eslint-disable-line
            APPLICATION_ID,
            APPLICATION_VERSION,
            APPLICATION_REGION,
            config,
        );

        if (session) {
            const data = JSON.parse(session);
            if (data.auth.authorisation_token && data.auth.role && awsRum) {
                const token_data = decodeJwtToken<NdrTokenData>(data.auth.authorisation_token);

                if (token_data) {
                    awsRum.addSessionAttributes({
                        ndrUserRole: data.auth.role,
                        ndrOdsName: token_data.selected_organisation.name,
                        ndrOdsCode: token_data.selected_organisation.org_ods_code,
                        ndrRoleCode: token_data.selected_organisation.role_code,
                        ndrSmartCardRole: token_data.smart_card_role,
                        ndrIsBSOL: token_data.selected_organisation.is_BSOL,
                        ndrSessionId: token_data.ndr_session_id,
                        ndrNHSUserId: token_data.nhs_user_id,
                    });
                }
            }
        }
    } catch (error) {
        console.log(error); // eslint-disable-line
    }
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
