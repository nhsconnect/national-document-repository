import { PatientDetails } from '../../types/generic/patientDetails';
import { ErrorResponse } from '../../types/generic/response';
import { SetSearchErrorCode } from '../../types/pages/patientSearchPage';
import axios from 'axios';

type Args = {
    setStatusCode: SetSearchErrorCode;
    nhsNumber: string;
    baseUrl: string;
};

type GetPatientDetailsResponse = {
    data: PatientDetails;
};

const getPatientDetails = async ({ setStatusCode, nhsNumber, baseUrl }: Args) => {
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
        const error = e as ErrorResponse;
        setStatusCode(error.response.status);
        return null;
    }
};

export default getPatientDetails;
