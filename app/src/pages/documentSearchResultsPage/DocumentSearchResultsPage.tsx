import React, { useEffect, useState } from 'react';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';
import PatientSummary from '../../components/generic/patientSummary/PatientSummary';
import { SearchResult } from '../../types/generic/searchResult';
import DocumentSearchResults from '../../components/blocks/documentSearch/DocumentSearchResults';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import { Link } from 'react-router-dom';
import { SUBMISSION_STATE } from '../../types/pages/documentSearchResultsPage/types';
import ProgressBar from '../../components/generic/progressBar/ProgressBar';
import SpinnerButton from '../../components/generic/spinnerButton/SpinnerButton';
import { Button } from 'nhsuk-react-components';
import getDocumentSearchResults from '../../helpers/requests/documentSearchResults';
import ServiceError from '../../components/layout/serviceErrorBox/ServiceErrorBox';

import { useBaseAPIUrl } from '../../providers/configProvider/ConfigProvider';

function DocumentSearchResultsPage() {
    const [patientDetails] = usePatientDetailsContext();
    const [searchResults, setSearchResults] = useState(Array<SearchResult>);
    const [submissionState, setSubmissionState] = useState(SUBMISSION_STATE.INITIAL);
    const [downloadState, setDownloadState] = useState(SUBMISSION_STATE.INITIAL);
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();

    useEffect(() => {
        if (!patientDetails?.nhsNumber) {
            navigate(routes.HOME);
        }

        const search = async () => {
            setSubmissionState(SUBMISSION_STATE.PENDING);
            setSearchResults([]);

            const nhsNumber: string = patientDetails?.nhsNumber || '';

            try {
                const results = await getDocumentSearchResults({
                    nhsNumber,
                    baseUrl,
                });

                if (results && results.length > 0) {
                    setSearchResults(results);
                }

                setSubmissionState(SUBMISSION_STATE.SUCCEEDED);
            } catch (e) {
                setSubmissionState(SUBMISSION_STATE.FAILED);
            }
        };

        void search();
    }, [patientDetails, setSearchResults, setSubmissionState, navigate, baseUrl]);

    const downloadAll = async () => {
        setDownloadState(SUBMISSION_STATE.PENDING);

        // Simulate delay for API call
        // Temporary, to be replaced with real changes from PRMDR-110
        setTimeout(() => {
            setDownloadState(SUBMISSION_STATE.SUCCEEDED);
        }, 2000);
    };

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
                            <p>
                                Only permanently delete all documents for this patient if you have a
                                valid reason to. For example, if the retention period of these
                                documents has been reached.
                            </p>
                            <div style={{ display: 'flex' }}>
                                {downloadState === SUBMISSION_STATE.PENDING ? (
                                    <SpinnerButton status="Downloading documents" />
                                ) : (
                                    <Button type="button" onClick={downloadAll}>
                                        Download All Documents
                                    </Button>
                                )}
                                <Link
                                    className="nhsuk-button nhsuk-button--secondary"
                                    style={{ marginLeft: 72 }}
                                    to={routes.DELETE_DOCUMENTS}
                                    role="button"
                                >
                                    Delete All Documents
                                </Link>
                            </div>
                            {downloadState === SUBMISSION_STATE.SUCCEEDED && (
                                <p>
                                    <strong>
                                        All documents have been successfully downloaded.
                                    </strong>
                                </p>
                            )}
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
