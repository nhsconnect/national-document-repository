import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import axios, { AxiosError } from 'axios';
import { OrganisationDetails } from '../../types/generic/organisationDetails';
import { types } from 'sass';
import List = types.List;

type Args = {
    username: string;
    password: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type GetOrganisationDetails = {
    data: Array<OrganisationDetails>;
};

const getOrganisationDetails = async ({ username, password, baseUrl, baseHeaders }: Args) => {
    const gatewayUrl = baseUrl + endpoints.ORGANISATION_SEARCH;

    try {
        const { data }: GetOrganisationDetails = await axios.get(gatewayUrl, {
            headers: {
                ...baseHeaders,
            },
            params: {
                username: username,
                password: password,
            },
        });
        return data;
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default getOrganisationDetails;
