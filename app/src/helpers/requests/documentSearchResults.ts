import { SearchResult } from '../../types/generic/searchResult';

import axios from 'axios';

type Args = {
    nhsNumber: string;
    baseUrl: string;
};

type GetDocumentSearchResultsResponse = {
    data: Array<SearchResult>;
};

const getDocumentSearchResults = async ({ nhsNumber, baseUrl }: Args) => {
    const gatewayUrl = baseUrl + '/SearchDocumentReferences';

    const { data }: GetDocumentSearchResultsResponse = await axios.get(gatewayUrl, {
        headers: {
            'Content-Type': 'application/json',
        },
        params: {
            patientId: nhsNumber,
        },
    });
    return data;
};

export default getDocumentSearchResults;
