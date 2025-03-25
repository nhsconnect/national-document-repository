import { AuthHeaders } from '../../types/blocks/authHeaders';
import axios, { AxiosError } from 'axios';
import { AccessAuditData, AccessAuditType } from '../../types/generic/accessAudit';

type Args = {
    accessAuditData: AccessAuditData;
    accessAuditType: AccessAuditType;
    baseUrl: string;
    baseHeaders: AuthHeaders;
    nhsNumber: string;
};

const postPatientAccessAudit = async ({
    accessAuditData,
    accessAuditType,
    baseUrl,
    baseHeaders,
    nhsNumber,
}: Args): Promise<void> => {
    const gatewayUrl = baseUrl + '/AccessAudit';

    try {
        await axios.post(gatewayUrl, accessAuditData, {
            headers: {
                ...baseHeaders,
            },
            params: {
                patientId: nhsNumber,
                accessAuditType,
            },
        });
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default postPatientAccessAudit;
