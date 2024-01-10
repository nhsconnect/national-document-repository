import React, { useEffect, useRef, useState } from 'react';
import PatientSummary from '../../components/generic/patientSummary/PatientSummary';
import { SearchResult } from '../../types/generic/searchResult';
import DocumentSearchResults from '../../components/blocks/documentSearchResults/DocumentSearchResults';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import { Link } from 'react-router-dom';
import { SUBMISSION_STATE } from '../../types/pages/documentSearchResultsPage/types';
import ProgressBar from '../../components/generic/progressBar/ProgressBar';
import ServiceError from '../../components/layout/serviceErrorBox/ServiceErrorBox';
import DocumentSearchResultsOptions from '../../components/blocks/documentSearchResultsOptions/DocumentSearchResultsOptions';
import { AxiosError } from 'axios';
import getDocumentSearchResults from '../../helpers/requests/getDocumentSearchResults';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import DeleteDocumentsStage from '../../components/blocks/deleteDocumentsStage/DeleteDocumentsStage';
import { DOCUMENT_TYPE } from '../../types/pages/UploadDocumentsPage/types';
import usePatient from '../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';

function DocumentSearchResultsPage() {
    const patientDetails = usePatient();

    const nhsNumber: string = patientDetails?.nhsNumber || '';
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
                    navigate(routes.START);
                }
                setSubmissionState(SUBMISSION_STATE.FAILED);
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

    return !isDeletingDocuments ? (
        <>
            <h1 id="download-page-title">Download electronic health records and attachments</h1>

            {(submissionState === SUBMISSION_STATE.FAILED ||
                downloadState === SUBMISSION_STATE.FAILED) && <ServiceError />}

            {<PatientSummary />}

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
                                numberOfFiles={searchResults.length}
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
    ) : (
        <DeleteDocumentsStage
            numberOfFiles={searchResults.length}
            setIsDeletingDocuments={setIsDeletingDocuments}
            docType={DOCUMENT_TYPE.ALL}
        />
    );
}

export default DocumentSearchResultsPage;
