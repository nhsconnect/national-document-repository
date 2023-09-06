import { PatientDetails } from '../../types/generic/patientDetails';
import { ErrorResponse } from '../../types/generic/response';
import { SetSearchErrorCode } from '../../types/pages/patientSearchPage';
import axios from 'axios';
import { buildPatientDetails } from '../test/testBuilders';

type Args = {
    setStatusCode: SetSearchErrorCode;
    nhsNumber: string;
    baseUrl: string;
};

type GetPatientDetailsResponse = {
    data: PatientDetails;
};

const getPatientDetails = async ({ nhsNumber, baseUrl }: Args) => {
    const isTestPatient = ['9000000009', '1000000001'].includes(nhsNumber);
    const isLocal =
        (!process.env.REACT_APP_ENVIRONMENT || process.env.REACT_APP_ENVIRONMENT === 'local') &&
        !isTestPatient;
    const gatewayUrl = baseUrl + '/SearchPatient';
    try {
        if (isLocal) {
            return buildPatientDetails({ nhsNumber });
        } else {
            const { data }: GetPatientDetailsResponse = await axios.get(gatewayUrl, {
                headers: {
                    'Content-Type': 'application/json',
                },
                params: {
                    patientId: nhsNumber,
                },
            });
            return data;
        }
    } catch (e) {
        const error = e as ErrorResponse;
        throw error;
    }
};

export default getPatientDetails;
