import { PatientDetails } from '../../types/generic/patientDetails';
import { SetSearchErrorCode } from '../../types/pages/patientSearchPage';
import axios, { AxiosError } from 'axios';

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
        throw error;
    }
};

export default getPatientDetails;
