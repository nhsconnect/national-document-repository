import axios from 'axios';

type Args = {
    nhsNumber: string;
    baseUrl: string;
};

type LloydGeorgeStitchResult = {
    number_of_files: number;
    totalFileSizeInByte: number;
    last_updated: string;
    presign_url: string;
};

async function getLloydGeorgeRecord({
    nhsNumber,
    baseUrl,
}: Args): Promise<LloydGeorgeStitchResult> {
    const gatewayUrl = baseUrl + '/LloydGeorgeStitch';

    const { data } = await axios.get(gatewayUrl, {
        headers: {
            'Content-Type': 'application/json',
        },
        params: {
            patientId: nhsNumber,
        },
    });
    return data;
}

export default getLloydGeorgeRecord;
