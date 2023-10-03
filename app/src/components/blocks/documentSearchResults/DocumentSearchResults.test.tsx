import { buildSearchResult } from '../../../helpers/test/testBuilders';
import { getFormattedDatetime } from '../../../helpers/utils/formatDatetime';
import { SearchResult } from '../../../types/generic/searchResult';
import DocumentSearchResults from './DocumentSearchResults';
import { render, screen, within } from '@testing-library/react';

describe('DocumentSearchResults', () => {
    const mockDetails = buildSearchResult();

    const mockSearchResults: Array<SearchResult> = [mockDetails];

    it('renders provided search results information', () => {
        render(<DocumentSearchResults searchResults={mockSearchResults} />);

        expect(screen.getByText('List of documents available')).toBeInTheDocument();
        const searchResults = screen.getAllByTestId('search-result');

        const mappedResults = searchResults.map((result) => ({
            filename: within(result).getByTestId('filename').textContent,
            created: within(result).getByTestId('created').textContent,
        }));

        expect(mappedResults).toEqual([
            {
                filename: mockDetails.fileName,
                created: getFormattedDatetime(new Date(mockDetails.created)),
            },
        ]);
    });

    it('renders provided search results in order of date', () => {
        const oldestDate = new Date(Date.UTC(2023, 7, 9, 10)).toISOString();
        const secondOldestDate = new Date(Date.UTC(2023, 7, 10, 10)).toISOString();
        const newestDate = new Date(Date.UTC(2023, 7, 11, 10)).toISOString();

        const mockSearchResults = [
            buildSearchResult({ created: oldestDate }),
            buildSearchResult({ created: newestDate }),
            buildSearchResult({ created: secondOldestDate }),
        ];

        render(<DocumentSearchResults searchResults={mockSearchResults} />);

        expect(screen.getByText('List of documents available')).toBeInTheDocument();

        const searchResults = screen.getAllByTestId('search-result');

        const mappedResults = searchResults.map((result) => ({
            created: within(result).getByTestId('created').textContent,
        }));

        expect(mappedResults).toEqual([
            { created: getFormattedDatetime(new Date(newestDate)) },
            { created: getFormattedDatetime(new Date(secondOldestDate)) },
            { created: getFormattedDatetime(new Date(oldestDate)) },
        ]);
    });
});
