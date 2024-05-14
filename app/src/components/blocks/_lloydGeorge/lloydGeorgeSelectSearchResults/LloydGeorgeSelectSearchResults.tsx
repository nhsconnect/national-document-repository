import { Button, Checkboxes, Table } from 'nhsuk-react-components';
import { SearchResult } from '../../../../types/generic/searchResult';
import { getFormattedDatetime } from '../../../../helpers/utils/formatDatetime';
import { Link, useNavigate } from 'react-router-dom';
import { routes } from '../../../../types/generic/routes';
import React, { Dispatch, SetStateAction, SyntheticEvent, useState } from 'react';
import { SEARCH_AND_DOWNLOAD_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import PatientSummary from '../../../generic/patientSummary/PatientSummary';

type Props = {
    searchResults: Array<SearchResult>;
    setSubmissionSearchState: Dispatch<SetStateAction<SEARCH_AND_DOWNLOAD_STATE>>;
    setSelectedDocuments: Dispatch<React.SetStateAction<Array<string>>>;
    selectedDocuments: Array<string>;
};

const LloydGeorgeSelectSearchResults = ({
    searchResults,
    setSubmissionSearchState,
    setSelectedDocuments,
    selectedDocuments,
}: Props) => {
    const sortMethod = (a: SearchResult, b: SearchResult) =>
        new Date(a.created) < new Date(b.created) ? 1 : -1;
    const navigate = useNavigate();
    const orderedResults = [...searchResults].sort(sortMethod);
    const tableCaption = <h2 style={{ fontSize: 32 }}>List of files in record</h2>;
    const [showNoOptionSelectedMessage, setShowNoOptionSelectedMessage] = useState<boolean>(false);
    const noOptionSelectedError = 'You must select a file to download or download all files';
    const pageHeader = 'Download the Lloyd George record for this patient';

    const handleChangeCheckboxes = (e: SyntheticEvent<HTMLInputElement>) => {
        const target = e.target as HTMLInputElement;

        if (target.checked) {
            setSelectedDocuments([...selectedDocuments, target.value]);
        } else {
            setSelectedDocuments(selectedDocuments.filter((e) => e !== target.value));
        }
    };
    const handleClickSelectedDownload = () => {
        if (selectedDocuments.length === searchResults.length) {
            console.log(
                'inside selected documents length equals search results length if statement',
            );
            console.log(searchResults);
            console.log(selectedDocuments);
            handleClickDownloadAll();
        } else if (selectedDocuments.length) {
            console.log('selected docs length: ' + selectedDocuments.length);
            console.log('selected docs length bool: ' + !!selectedDocuments.length);
            console.log('inside selected documents if statement ' + selectedDocuments);
            setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.DOWNLOAD_SELECTED);
        } else {
            setShowNoOptionSelectedMessage(true);
            window.scrollTo(0, 0);
        }
    };
    const handleClickDownloadAll = () => {
        setSelectedDocuments([]);
        setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.DOWNLOAD_SELECTED);
    };

    return (
        <>
            {showNoOptionSelectedMessage && (
                <ErrorBox
                    messageTitle={'There is a problem '}
                    messageLinkBody={noOptionSelectedError}
                    errorBoxSummaryId={'error-box-summary'}
                    errorInputLink={'#available-files-table-title'}
                    dataTestId={'download-selection-error-box'}
                />
            )}
            <h1 id="download-page-title">{pageHeader}</h1>
            <PatientSummary />

            <Table
                id="available-files-table-title"
                data-testid="available-files-table-title"
                caption={tableCaption}
            >
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
                                <Checkboxes onChange={handleChangeCheckboxes}>
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
                <Button
                    onClick={handleClickSelectedDownload}
                    data-testid="download-selected-files-btn"
                >
                    Download selected files
                </Button>
                <Button
                    onClick={handleClickDownloadAll}
                    className={'nhsuk-button nhsuk-button--secondary'}
                    style={{ marginLeft: 18 }}
                    data-testid="download-all-files-btn"
                >
                    Download all files
                </Button>
                <Link
                    id="start-again-link"
                    data-testid="start-again-link"
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
