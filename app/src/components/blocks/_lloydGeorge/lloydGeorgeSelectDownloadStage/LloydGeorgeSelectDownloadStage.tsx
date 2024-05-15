import React, { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../../helpers/hooks/usePatient';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import { useNavigate } from 'react-router-dom';
import useTitle from '../../../../helpers/hooks/useTitle';
import { SearchResult } from '../../../../types/generic/searchResult';
import { SEARCH_AND_DOWNLOAD_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import getDocumentSearchResults from '../../../../helpers/requests/getDocumentSearchResults';
import { AxiosError } from 'axios';
import { routes } from '../../../../types/generic/routes';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import ProgressBar from '../../../generic/progressBar/ProgressBar';
import { DOCUMENT_TYPE } from '../../../../types/pages/UploadDocumentsPage/types';
import { isMock } from '../../../../helpers/utils/isLocal';
import LloydGeorgeSelectSearchResults from '../lloydGeorgeSelectSearchResults/LloydGeorgeSelectSearchResults';
import PatientSummary from '../../../generic/patientSummary/PatientSummary';
import LloydGeorgeDownloadStage from '../lloydGeorgeDownloadAllStage/LloydGeorgeDownloadStage';

export type Props = {
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    deleteAfterDownload: boolean;
    setDownloadStage: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
};

function LloydGeorgeSelectDownloadStage({
    setStage,
    deleteAfterDownload = false,
    setDownloadStage,
}: Props) {
    const mounted = useRef(false);
    const navigate = useNavigate();
    const patientDetails = usePatient();
    const nhsNumber = patientDetails?.nhsNumber ?? '';
    const pageHeader = 'Download the Lloyd George record for this patient';
    const [searchResults, setSearchResults] = useState<Array<SearchResult>>([]);
    const [submissionSearchState, setSubmissionSearchState] = useState(
        SEARCH_AND_DOWNLOAD_STATE.INITIAL,
    );
    const [selectedDocuments, setSelectedDocuments] = useState<Array<string>>([]);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    useTitle({ pageTitle: pageHeader });

    useEffect(() => {
        const onPageLoad = async () => {
            setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.SEARCH_PENDING);

            try {
                const results = await getDocumentSearchResults({
                    nhsNumber,
                    baseUrl,
                    baseHeaders,
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                });
                setSearchResults(results ?? []);

                setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.SEARCH_SUCCEEDED);
            } catch (e) {
                const error = e as AxiosError;
                if (isMock(error)) {
                    setSearchResults([
                        {
                            fileName: '2of3_testy_test.pdf',
                            created: '2024-05-07T14:52:00.827602Z',
                            virusScannerResult: 'Clean',
                            ID: 'test-id-2',
                        },
                        {
                            fileName: '1of3_testy_test.pdf',
                            created: '2024-05-07T14:52:00.827602Z',
                            virusScannerResult: 'Clean',
                            ID: 'test-id',
                        },
                        {
                            fileName: '3of3_testy_test.pdf',
                            created: '2024-05-07T14:52:00.827602Z',
                            virusScannerResult: 'Clean',
                            ID: 'test-id-3',
                        },
                        {
                            fileName: '2of3_earlier_creation_date.pdf',
                            created: '2024-05-07T13:52:00.827602Z',
                            virusScannerResult: 'Clean',
                            ID: 'test-id-2',
                        },
                        {
                            fileName: '1of3_earlier_creation_date.pdf',
                            created: '2024-05-07T13:52:00.827602Z',
                            virusScannerResult: 'Clean',
                            ID: 'test-id',
                        },
                        {
                            fileName: '3of3_earlier_creation_date.pdf',
                            created: '2024-05-07T13:52:00.827602Z',
                            virusScannerResult: 'Clean',
                            ID: 'test-id-3',
                        },
                        {
                            fileName: '11of20_earlier_creation_date.pdf',
                            created: '2024-05-07T13:52:00.827602Z',
                            virusScannerResult: 'Clean',
                            ID: 'test-id-3',
                        },
                    ]);
                    setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.SEARCH_SUCCEEDED);
                } else if (error.response?.status === 403) {
                    navigate(routes.SESSION_EXPIRED);
                } else if (error.response?.status && error.response?.status >= 500) {
                    navigate(routes.SERVER_ERROR + errorToParams(error));
                } else {
                    setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.SEARCH_FAILED);
                }
            }
        };
        if (!mounted.current) {
            mounted.current = true;
            void onPageLoad();
        }
    }, [
        patientDetails,
        searchResults,
        nhsNumber,
        setSearchResults,
        navigate,
        baseUrl,
        baseHeaders,
    ]);

    return (
        <>
            {submissionSearchState === SEARCH_AND_DOWNLOAD_STATE.SEARCH_PENDING && (
                <>
                    <h1 id="download-page-title">{pageHeader}</h1>
                    <PatientSummary />
                    <ProgressBar status="Loading..."></ProgressBar>
                </>
            )}
            {submissionSearchState === SEARCH_AND_DOWNLOAD_STATE.SEARCH_SUCCEEDED &&
                searchResults.length && (
                    <LloydGeorgeSelectSearchResults
                        searchResults={searchResults}
                        setSubmissionSearchState={setSubmissionSearchState}
                        setSelectedDocuments={setSelectedDocuments}
                        selectedDocuments={selectedDocuments}
                    />
                )}
            {submissionSearchState === SEARCH_AND_DOWNLOAD_STATE.DOWNLOAD_SELECTED && (
                <LloydGeorgeDownloadStage
                    setStage={setStage}
                    deleteAfterDownload={deleteAfterDownload}
                    selectedDocuments={selectedDocuments}
                    searchResults={searchResults}
                    numberOfFiles={searchResults.length}
                    setDownloadStage={setDownloadStage}
                />
            )}
        </>
    );
}

export default LloydGeorgeSelectDownloadStage;
