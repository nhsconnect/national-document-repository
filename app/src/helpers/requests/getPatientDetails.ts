import { PatientDetails } from '../../types/generic/patientDetails';
import axios, { AxiosError } from 'axios';
import { endpoints } from '../../types/generic/endpoints';
type Args = {
    nhsNumber: string;
    baseUrl: string;
};

type GetPatientDetailsResponse = {
    data: PatientDetails;
};

const getPatientDetails = async ({ nhsNumber, baseUrl }: Args) => {
    const gatewayUrl = baseUrl + endpoints.PATIENT_SEARCH;
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
