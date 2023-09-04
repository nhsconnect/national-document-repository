import { ErrorResponse } from '../../types/generic/response';
import { SetSearchErrorCode } from '../../types/pages/patientSearchPage';
import { buildPatientDetails } from '../test/testBuilders';

type Args = {
    setStatusCode: SetSearchErrorCode;
    nhsNumber: string;
};

const getPatientDetails = async ({ setStatusCode, nhsNumber }: Args) => {
    try {
        await new Promise((resolve) => {
            setTimeout(() => {
                resolve(null);
            }, 2000);
        });
        return buildPatientDetails();
    } catch (e) {
        const error = e as ErrorResponse;
        setStatusCode(error.response.status);
        return null;
    }
};

export default getPatientDetails;
