import { PatientDetails } from '../../types/generic/patientDetails';
import { SetSearchErrorCode } from '../../types/pages/patientSearchPage';
import axios, { AxiosError } from 'axios';
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
    const gatewayUrl = baseUrl + '/SearchPatient';
    try {
        const { data }: GetPatientDetailsResponse = await axios.get(gatewayUrl, {
            headers: {
                'Content-Type': 'application/json',
            },
            params: {
                patientId: nhsNumber,
            },
        });
        return data;
    } catch (e) {
        const error = e as AxiosError;
        const isLocal =
            !process.env.REACT_APP_ENVIRONMENT || process.env.REACT_APP_ENVIRONMENT === 'local';
        if (isLocal) {
            return buildPatientDetails({ nhsNumber });
        } else {
            throw error;
        }
    }
};

export default getPatientDetails;
