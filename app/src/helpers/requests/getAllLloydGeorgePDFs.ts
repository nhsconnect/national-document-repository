import { AxiosError } from 'axios';
import axios from 'axios';
import { endpoints } from '../../types/generic/endpoints';
import { AuthHeaders } from '../../types/blocks/authHeaders';

type Args = {
    baseUrl: string;
    baseHeaders: AuthHeaders;
    nhsNumber: string;
};

type GetAllLloydGeorgePDFsResponse = {
    last_updated: string;
    number_of_files: number;
    presign_url: string;
    total_file_size_in_byte: number;
};

const getAllLloydGeorgePDFs = async ({ baseUrl, baseHeaders, nhsNumber }: Args) => {
    const gatewayUrl = baseUrl + endpoints.LG_STITCH;
    try {
        const response = await axios.get(gatewayUrl, {
            headers: {
                ...baseHeaders,
            },
            params: {
                patientId: nhsNumber,
            },
        });
        const data: GetAllLloydGeorgePDFsResponse = response.data;
        return data;
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default getAllLloydGeorgePDFs;
