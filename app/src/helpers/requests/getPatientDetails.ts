import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import { PatientDetails } from '../../types/generic/patientDetails';
import axios, { AxiosError } from 'axios';

type Args = {
    nhsNumber: string;
    baseUrl: string;
    authHeaders: AuthHeaders;
};

type GetPatientDetailsResponse = {
    data: PatientDetails;
};

const getPatientDetails = async ({ nhsNumber, baseUrl, authHeaders }: Args) => {
    const gatewayUrl = baseUrl + endpoints.PATIENT_SEARCH;
    try {
        const { data }: GetPatientDetailsResponse = await axios.get(gatewayUrl, {
            headers: authHeaders,
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
