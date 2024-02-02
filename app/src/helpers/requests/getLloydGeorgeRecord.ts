import axios from 'axios';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';

type Args = {
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

export type LloydGeorgeStitchResult = {
    number_of_files: number;
    total_file_size_in_byte: number;
    last_updated: string;
    presign_url: string;
};

async function getLloydGeorgeRecord({
    nhsNumber,
    baseUrl,
    baseHeaders,
}: Args): Promise<LloydGeorgeStitchResult> {
    const gatewayUrl = baseUrl + endpoints.LLOYDGEORGE_STITCH;

    const { data } = await axios.get(gatewayUrl, {
        headers: {
            ...baseHeaders,
        },
        params: {
            patientId: nhsNumber,
        },
    });
    return data;
}

export default getLloydGeorgeRecord;
