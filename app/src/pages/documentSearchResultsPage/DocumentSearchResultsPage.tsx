import React, { useEffect, useRef, useState } from 'react';
import PatientSummary from '../../components/generic/patientSummary/PatientSummary';
import { SearchResult } from '../../types/generic/searchResult';
import DocumentSearchResults from '../../components/blocks/_arf/documentSearchResults/DocumentSearchResults';
import { Outlet, Route, Routes, useNavigate } from 'react-router';
import { routeChildren, routes } from '../../types/generic/routes';
import { Link } from 'react-router-dom';
import { SUBMISSION_STATE } from '../../types/pages/documentSearchResultsPage/types';
import ProgressBar from '../../components/generic/progressBar/ProgressBar';
import ServiceError from '../../components/layout/serviceErrorBox/ServiceErrorBox';
import DocumentSearchResultsOptions from '../../components/blocks/_arf/documentSearchResultsOptions/DocumentSearchResultsOptions';
import { AxiosError } from 'axios';
import getDocumentSearchResults from '../../helpers/requests/getDocumentSearchResults';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import DeleteDocumentsStage from '../../components/blocks/deleteDocumentsStage/DeleteDocumentsStage';
import { DOCUMENT_TYPE } from '../../types/pages/UploadDocumentsPage/types';
import usePatient from '../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import ErrorBox from '../../components/layout/errorBox/ErrorBox';
import { errorToParams } from '../../helpers/utils/errorToParams';
import useTitle from '../../helpers/hooks/useTitle';
import { getLastURLPath } from '../../helpers/utils/urlManipulations';

function DocumentSearchResultsPage() {
    const patientDetails = usePatient();

    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const [searchResults, setSearchResults] = useState<Array<SearchResult>>([]);
    const [submissionState, setSubmissionState] = useState(SUBMISSION_STATE.INITIAL);
    const [downloadState, setDownloadState] = useState(SUBMISSION_STATE.INITIAL);
    const [isDeletingDocuments, setIsDeletingDocuments] = useState(false);
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();

    const handleUpdateDownloadState = (newState: SUBMISSION_STATE) => {
        setDownloadState(newState);
    };

    const mounted = useRef(false);
    useEffect(() => {
        const onPageLoad = async () => {
            setSubmissionState(SUBMISSION_STATE.PENDING);

            try {
                const results = await getDocumentSearchResults({
                    nhsNumber,
                    baseUrl,
                    baseHeaders,
                });
                setSearchResults(results ?? []);

                setSubmissionState(SUBMISSION_STATE.SUCCEEDED);
            } catch (e) {
                const error = e as AxiosError;
                if (error.response?.status === 403) {
                    navigate(routes.SESSION_EXPIRED);
                } else if (error.response?.status && error.response?.status >= 500) {
                    navigate(routes.SERVER_ERROR + errorToParams(error));
                } else {
                    setSubmissionState(SUBMISSION_STATE.FAILED);
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
        setSubmissionState,
        isDeletingDocuments,
        navigate,
        baseUrl,
        baseHeaders,
    ]);
    const pageHeader = 'Download electronic health records and attachments';
    useTitle({ pageTitle: pageHeader });

    const PageIndexView = () => (
        <>
            <h1 id="download-page-title">{pageHeader}</h1>

            {(submissionState === SUBMISSION_STATE.FAILED ||
                downloadState === SUBMISSION_STATE.FAILED) && <ServiceError />}

            <PatientSummary />

            {submissionState === SUBMISSION_STATE.PENDING && (
                <ProgressBar status="Loading..."></ProgressBar>
            )}

            {submissionState === SUBMISSION_STATE.SUCCEEDED && (
                <>
                    {searchResults.length && patientDetails ? (
                        <>
                            <DocumentSearchResults searchResults={searchResults} />
                            <DocumentSearchResultsOptions
                                nhsNumber={nhsNumber}
                                downloadState={downloadState}
                                updateDownloadState={handleUpdateDownloadState}
                                setIsDeletingDocuments={setIsDeletingDocuments}
                            />
                        </>
                    ) : (
                        <p>
                            <strong id="no-files-message">
                                There are no documents available for this patient.
                            </strong>
                        </p>
                    )}
                </>
            )}

            {downloadState === SUBMISSION_STATE.FAILED && (
                <ErrorBox
                    messageTitle={'There is a problem with the documents'}
                    messageBody={'An error has occurred while preparing your download'}
                    errorBoxSummaryId={'error-box-summary'}
                />
            )}

            {(submissionState === SUBMISSION_STATE.FAILED ||
                submissionState === SUBMISSION_STATE.SUCCEEDED) && (
                <p>
                    <Link
                        id="start-again-link"
                        to=""
                        onClick={(e) => {
                            e.preventDefault();
                            navigate(routes.START);
                        }}
                    >
                        Start Again
                    </Link>
                </p>
            )}
        </>
    );

    return (
        <>
            <div>
                <Routes>
                    <Route index element={<PageIndexView />} />
                    <Route
                        path={getLastURLPath(routeChildren.ARF_DELETE) + '/*'}
                        element={
                            <DeleteDocumentsStage
                                numberOfFiles={searchResults.length}
                                setIsDeletingDocuments={setIsDeletingDocuments}
                                docType={DOCUMENT_TYPE.ALL}
                            />
                        }
                    />
                </Routes>

                <Outlet />
            </div>
        </>
    );
}

export default DocumentSearchResultsPage;
