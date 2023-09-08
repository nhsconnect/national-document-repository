import { Table } from 'nhsuk-react-components';
import { SearchResult } from '../../../types/generic/searchResult';
import { useState } from 'react';
import { getFormattedDatetime } from '../../../helpers/utils/formatDatetime';

type Props = {
    searchResults: Array<SearchResult>;
};

const DocumentSearchResults = (props: Props) => {
    const sortMethod = (a: SearchResult, b: SearchResult) =>
        new Date(a.created) < new Date(b.created) ? 1 : -1;

    const orderedResults = props.searchResults.sort(sortMethod);
    const [searchResults, ,] = useState(orderedResults);

    return (
        <>
            <Table caption=<h2 style={{ fontSize: 32 }}>List of documents available</h2>>
                <Table.Head>
                    <Table.Row>
                        <Table.Cell className={'table-column-header'}>Filename</Table.Cell>
                        <Table.Cell className={'table-column-header'}>Uploaded At</Table.Cell>
                    </Table.Row>
                </Table.Head>
                <Table.Body>
                    {searchResults.map((result, index) => (
                        <Table.Row key={`document-${index}`} data-testid="search-result">
                            <Table.Cell data-testid="filename">{result.fileName}</Table.Cell>
                            <Table.Cell data-testid="created">
                                {getFormattedDatetime(new Date(result.created))}
                            </Table.Cell>
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>
        </>
    );
};

export default DocumentSearchResults;
