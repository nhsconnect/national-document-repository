import React, { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import usePatient from '../../../../helpers/hooks/usePatient';
import { Outlet, Route, Routes, useNavigate } from 'react-router-dom';
import useTitle from '../../../../helpers/hooks/useTitle';
import { SearchResult } from '../../../../types/generic/searchResult';
import { SEARCH_AND_DOWNLOAD_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import getDocumentSearchResults from '../../../../helpers/requests/getDocumentSearchResults';
import { AxiosError } from 'axios';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import ProgressBar from '../../../generic/progressBar/ProgressBar';
import { DOCUMENT_TYPE } from '../../../../types/pages/UploadDocumentsPage/types';
import { isMock } from '../../../../helpers/utils/isLocal';
import LloydGeorgeSelectSearchResults from '../lloydGeorgeSelectSearchResults/LloydGeorgeSelectSearchResults';
import PatientSummary from '../../../generic/patientSummary/PatientSummary';
import LloydGeorgeDownloadStage from '../lloydGeorgeDownloadStage/LloydGeorgeDownloadStage';
import { buildSearchResult } from '../../../../helpers/test/testBuilders';
import { getLastURLPath } from '../../../../helpers/utils/urlManipulations';
import LgDownloadComplete from '../lloydGeorgeDownloadComplete/LloydGeorgeDownloadComplete';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';

export type Props = {
    deleteAfterDownload?: boolean;
    numberOfFiles: number;
    setDownloadStage: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
};

function LloydGeorgeSelectDownloadStage({
    setDownloadStage,
    numberOfFiles,
    deleteAfterDownload = false,
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
    let numberOfFilesForDownload = useRef(numberOfFiles);

    useTitle({ pageTitle: pageHeader });

    useEffect(() => {
        const onPageLoad = async () => {
            setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.SEARCH_PENDING);

            try {
                // This check is in place for when we navigate directly to a full download,
                // in that instance we do not need to get a list of selectable files as we will download all files
                if (window.location.href === baseUrl + routeChildren.LLOYD_GEORGE_DOWNLOAD) {
                    const results = await getDocumentSearchResults({
                        nhsNumber,
                        baseUrl,
                        baseHeaders,
                        docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    });
                    setSearchResults(results ?? []);
                    numberOfFilesForDownload.current = searchResults.length;
                    setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.SEARCH_SUCCEEDED);
                }
            } catch (e) {
                const error = e as AxiosError;
                if (isMock(error)) {
                    setSearchResults([
                        buildSearchResult(),
                        buildSearchResult({ fileName: 'fileName2.pdf', ID: '1234qwer-241ewewr-2' }),
                    ]);
                    setSubmissionSearchState(SEARCH_AND_DOWNLOAD_STATE.SEARCH_SUCCEEDED);
                } else if (error.response?.status === 403) {
                    navigate(routes.SESSION_EXPIRED);
                } else {
                    navigate(routes.SERVER_ERROR + errorToParams(error));
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

    const PageIndexView = () => (
        <>
            {submissionSearchState === SEARCH_AND_DOWNLOAD_STATE.SEARCH_PENDING && (
                <>
                    <h1 id="download-page-title">{pageHeader}</h1>
                    <PatientSummary />
                    <ProgressBar status="Loading..."></ProgressBar>
                </>
            )}
            {submissionSearchState === SEARCH_AND_DOWNLOAD_STATE.SEARCH_SUCCEEDED &&
                !!searchResults.length && (
                    <LloydGeorgeSelectSearchResults
                        searchResults={searchResults}
                        setSubmissionSearchState={setSubmissionSearchState}
                        setSelectedDocuments={setSelectedDocuments}
                        selectedDocuments={selectedDocuments}
                    />
                )}
        </>
    );

    return (
        <>
            {/* <div id="here">{window.location.href}</div>
            <div id="here2">
                {window.location.href === baseUrl + routeChildren.LLOYD_GEORGE_DOWNLOAD}
            </div> */}
            <Routes>
                <Route index element={<PageIndexView />} />
                <Route
                    path={getLastURLPath(routeChildren.LLOYD_GEORGE_DOWNLOAD_IN_PROGRESS)}
                    element={
                        <LloydGeorgeDownloadStage
                            deleteAfterDownload={deleteAfterDownload}
                            selectedDocuments={selectedDocuments}
                            searchResults={searchResults}
                            numberOfFiles={numberOfFilesForDownload.current}
                            setDownloadStage={setDownloadStage}
                        />
                    }
                />
                <Route
                    path={getLastURLPath(routeChildren.LLOYD_GEORGE_DOWNLOAD_COMPLETE)}
                    element={
                        <LgDownloadComplete
                            deleteAfterDownload={deleteAfterDownload}
                            numberOfFiles={numberOfFilesForDownload.current}
                            selectedDocuments={selectedDocuments}
                            searchResults={searchResults}
                            setDownloadStage={setDownloadStage}
                        />
                    }
                />
            </Routes>

            <Outlet />
        </>
    );
}

export default LloydGeorgeSelectDownloadStage;
