import { endpoints } from '../../types/generic/endpoints';
import { PatientDetails } from '../../types/generic/patientDetails';
import { AxiosError, AxiosInstance } from 'axios';

type Args = {
    nhsNumber: string;
    axios: AxiosInstance;
};

type GetPatientDetailsResponse = {
    data: PatientDetails;
};

const getPatientDetails = async ({ nhsNumber, axios }: Args) => {
    const gatewayUrl = endpoints.PATIENT_SEARCH;

    try {
        const { data }: GetPatientDetailsResponse = await axios.get(gatewayUrl, {
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
