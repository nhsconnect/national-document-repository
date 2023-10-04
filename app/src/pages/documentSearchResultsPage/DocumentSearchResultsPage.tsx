import React, { useEffect, useState } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import PatientSummary from '../../components/generic/patientSummary/PatientSummary';
import { SearchResult } from '../../types/generic/searchResult';
import DocumentSearchResults from '../../components/blocks/documentSearchResults/DocumentSearchResults';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import { Link } from 'react-router-dom';
import { SUBMISSION_STATE } from '../../types/pages/documentSearchResultsPage/types';
import ProgressBar from '../../components/generic/progressBar/ProgressBar';
import ServiceError from '../../components/layout/serviceErrorBox/ServiceErrorBox';

import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';
import DocumentSearchResultsOptions from '../../components/blocks/documentSearchResultsOptions/DocumentSearchResultsOptions';
import { AxiosError } from 'axios';
import getDocumentSearchResults from '../../helpers/requests/documentSearchResults';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';

function DocumentSearchResultsPage() {
    const [patientDetails] = usePatientDetailsContext();

    const nhsNumber: string = patientDetails?.nhsNumber || '';
    const [searchResults, setSearchResults] = useState<Array<SearchResult>>([]);
    const [submissionState, setSubmissionState] = useState(SUBMISSION_STATE.INITIAL);
    const [downloadState, setDownloadState] = useState(SUBMISSION_STATE.INITIAL);
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const handleUpdateDownloadState = (newState: SUBMISSION_STATE) => {
        setDownloadState(newState);
    };

    useEffect(() => {
        const search = async () => {
            setSubmissionState(SUBMISSION_STATE.PENDING);

            try {
                const results = await getDocumentSearchResults({
                    nhsNumber,
                    baseUrl,
                    baseHeaders,
                });
                setSearchResults(results);

                setSubmissionState(SUBMISSION_STATE.SUCCEEDED);
            } catch (e) {
                const error = e as AxiosError;
                if (error.response?.status === 403) {
                    navigate(routes.HOME);
                }
                setSubmissionState(SUBMISSION_STATE.FAILED);
            }
        };
        if (searchResults && searchResults.length > 0 && nhsNumber) {
            void search();
        }
    }, [
        patientDetails,
        searchResults,
        nhsNumber,
        setSearchResults,
        setSubmissionState,
        navigate,
        baseUrl,
        baseHeaders,
    ]);

    return (
        <>
            <h1 id="download-page-title">Download electronic health records and attachments</h1>

            {(submissionState === SUBMISSION_STATE.FAILED ||
                downloadState === SUBMISSION_STATE.FAILED) && <ServiceError />}

            {patientDetails && <PatientSummary patientDetails={patientDetails} />}

            {submissionState === SUBMISSION_STATE.PENDING && (
                <ProgressBar status="Loading..."></ProgressBar>
            )}

            {submissionState === SUBMISSION_STATE.SUCCEEDED && (
                <>
                    {searchResults.length > 0 && (
                        <>
                            <DocumentSearchResults searchResults={searchResults} />
                            <DocumentSearchResultsOptions
                                nhsNumber={nhsNumber}
                                downloadState={downloadState}
                                updateDownloadState={handleUpdateDownloadState}
                            />
                        </>
                    )}

                    {searchResults.length === 0 && (
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
                            navigate(routes.HOME);
                        }}
                    >
                        Start Again
                    </Link>
                </p>
            )}
        </>
    );
}

export default DocumentSearchResultsPage;
