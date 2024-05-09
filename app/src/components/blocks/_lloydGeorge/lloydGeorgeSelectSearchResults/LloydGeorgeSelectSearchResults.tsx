import { Button, ButtonLink, Checkboxes, Table } from 'nhsuk-react-components';
import { SearchResult } from '../../../../types/generic/searchResult';
import { getFormattedDatetime } from '../../../../helpers/utils/formatDatetime';
import { Link, useNavigate } from 'react-router-dom';
import { routes } from '../../../../types/generic/routes';
import React, { Dispatch, FormEventHandler, SetStateAction, SyntheticEvent } from 'react';
import { SEARCH_AND_DOWNLOAD_STATE } from '../../../../types/pages/documentSearchResultsPage/types';

type Props = {
    searchResults: Array<SearchResult>;
    setSubmissionSearchState: Dispatch<SetStateAction<SEARCH_AND_DOWNLOAD_STATE>>;
    setSelectedDocuments: Dispatch<React.SetStateAction<string[]>>;
    selectedDocuments: string[];
};

const LloydGeorgeSelectSearchResults = (props: Props) => {
    const sortMethod = (a: SearchResult, b: SearchResult) =>
        new Date(a.created) < new Date(b.created) ? 1 : -1;
    const navigate = useNavigate();
    const orderedResults = [...props.searchResults].sort(sortMethod);
    const tableCaption = <h2 style={{ fontSize: 32 }}>List of documents available</h2>;
    const onChangeHandler = (e: SyntheticEvent<HTMLInputElement>) => {
        console.log('before ' + props.selectedDocuments);
        const target = e.target as HTMLInputElement;

        if (target.checked) {
            props.setSelectedDocuments([...props.selectedDocuments, target.value]);
        } else {
            props.setSelectedDocuments(props.selectedDocuments.filter((e) => e !== target.value));
        }
        console.log('after ' + props.selectedDocuments);
    };
    console.log('outside ' + props.selectedDocuments);

    return (
        <>
            <Table id="available-files-table-title" caption={tableCaption}>
                <Table.Head>
                    <Table.Row>
                        <Table.Cell className={'table-column-header'}>Selected</Table.Cell>
                        <Table.Cell className={'table-column-header'}>Filename</Table.Cell>
                        <Table.Cell className={'table-column-header'}>Upload date</Table.Cell>
                    </Table.Row>
                </Table.Head>
                <Table.Body>
                    {orderedResults.map((result, index) => (
                        <Table.Row
                            className={'available-files-row'}
                            id={'available-files-row-' + index}
                            key={`document-${result.fileName + result.created}`}
                            data-testid="search-result"
                        >
                            <Table.Cell
                                id={'selected-files-row-' + index + ''}
                                data-testid="select"
                            >
                                <Checkboxes onChange={onChangeHandler}>
                                    <Checkboxes.Box value={result.id}> </Checkboxes.Box>
                                </Checkboxes>{' '}
                            </Table.Cell>
                            <Table.Cell
                                id={'available-files-row-' + index + '-filename'}
                                data-testid="filename"
                            >
                                {result.fileName}
                            </Table.Cell>
                            <Table.Cell
                                id={'available-files-row-' + index + '-created-date'}
                                data-testid="created"
                            >
                                {getFormattedDatetime(new Date(result.created))}
                            </Table.Cell>
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>
            <div style={{ display: 'flex', alignItems: 'baseline' }}>
                <Button type="submit" id="verify-submit">
                    Download selected files
                </Button>
                <ButtonLink
                    className={'nhsuk-button nhsuk-button--secondary'}
                    style={{ marginLeft: 18 }}
                >
                    Download all files
                </ButtonLink>
                <Link
                    id="start-again-link"
                    to=""
                    onClick={(e) => {
                        e.preventDefault();
                        navigate(routes.START);
                    }}
                    style={{ marginLeft: 18 }}
                >
                    Start Again
                </Link>
            </div>
        </>
    );
};

export default LloydGeorgeSelectSearchResults;
