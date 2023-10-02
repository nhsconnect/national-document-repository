import axios from 'axios';

type Args = {
    nhsNumber: string;
    baseUrl: string;
};

type GetPresignedUrl = {
    data: string;
};

const getPresignedUrlForZip = async ({ nhsNumber, baseUrl }: Args) => {
    const gatewayUrl = baseUrl + '/DocumentManifestByNHSNumber';

    const { data }: GetPresignedUrl = await axios.get(gatewayUrl, {
        headers: {
            'Content-Type': 'application/json',
        },
        params: {
            patientId: nhsNumber,
        },
    });
    return data;
};

export default getPresignedUrlForZip;
