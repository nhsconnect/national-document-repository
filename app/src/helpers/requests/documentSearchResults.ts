import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import { SearchResult } from '../../types/generic/searchResult';

import axios, { AxiosError } from 'axios';

type Args = {
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type GetDocumentSearchResultsResponse =
    | {
          data: Array<SearchResult>;
      }
    | undefined;

const getDocumentSearchResults = async ({ nhsNumber, baseUrl, baseHeaders }: Args) => {
    const gatewayUrl = baseUrl + endpoints.DOCUMENT_SEARCH;

    try {
        const response: GetDocumentSearchResultsResponse = await axios.get(gatewayUrl, {
            headers: {
                ...baseHeaders,
            },
            params: {
                patientId: nhsNumber,
            },
        });
        return response?.data;
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default getDocumentSearchResults;
