import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import { SearchResult } from '../../types/generic/searchResult';

import axios from 'axios';

type Args = {
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type GetDocumentSearchResultsResponse = {
    data: Array<SearchResult>;
};

const getDocumentSearchResults = async ({ nhsNumber, baseUrl, baseHeaders }: Args) => {
    const gatewayUrl = baseUrl + endpoints.DOCUMENT_SEARCH;

    const { data }: GetDocumentSearchResultsResponse = await axios.get(gatewayUrl, {
        headers: {
            ...baseHeaders,
        },
        params: {
            patientId: nhsNumber,
        },
    });
    return data;
};

export default getDocumentSearchResults;
