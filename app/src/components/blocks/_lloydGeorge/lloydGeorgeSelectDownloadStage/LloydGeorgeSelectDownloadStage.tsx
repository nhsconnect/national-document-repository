import { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../../helpers/hooks/usePatient';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import { Link, useNavigate } from 'react-router-dom';
import useTitle from '../../../../helpers/hooks/useTitle';
import { SearchResult } from '../../../../types/generic/searchResult';
import { SUBMISSION_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import getDocumentSearchResults from '../../../../helpers/requests/getDocumentSearchResults';
import { AxiosError } from 'axios';
import { routes } from '../../../../types/generic/routes';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import ServiceError from '../../../layout/serviceErrorBox/ServiceErrorBox';
import ProgressBar from '../../../generic/progressBar/ProgressBar';
import DocumentSearchResults from '../../_arf/documentSearchResults/DocumentSearchResults';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import { DOCUMENT_TYPE } from '../../../../types/pages/UploadDocumentsPage/types';
import { isMock } from '../../../../helpers/utils/isLocal';

export type Props = {
    numberOfFiles: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    deleteAfterDownload: boolean;
    setDownloadStage: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
};

function LloydGeorgeSelectDownloadStage({
    numberOfFiles,
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
    const [submissionState, setSubmissionState] = useState(SUBMISSION_STATE.INITIAL);
    const [downloadState, setDownloadState] = useState(SUBMISSION_STATE.INITIAL);
    const [isDeletingDocuments, setIsDeletingDocuments] = useState(false);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    useTitle({ pageTitle: pageHeader });

    const handleUpdateDownloadState = (newState: SUBMISSION_STATE) => {
        setDownloadState(newState);
    };

    useEffect(() => {
        const onPageLoad = async () => {
            setSubmissionState(SUBMISSION_STATE.PENDING);

            try {
                const results = await getDocumentSearchResults({
                    nhsNumber,
                    baseUrl,
                    baseHeaders,
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                });
                setSearchResults(results ?? []);

                setSubmissionState(SUBMISSION_STATE.SUCCEEDED);
            } catch (e) {
                const error = e as AxiosError;
                if (isMock(error)) {
                    setSearchResults([
                        {
                            fileName: 'testy_test.pdf',
                            created: '2024-05-07T14:52:00.827602Z',
                            virusScannerResult: 'Clean',
                        },
                    ]);
                    setSubmissionState(SUBMISSION_STATE.SUCCEEDED);
                } else if (error.response?.status === 403) {
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

    return (
        <>
            <div
                className="lloydgeorge_downloadall-stage"
                data-testid="lloydgeorge_downloadall-stage"
            >
                <div className="lloydgeorge_downloadall-stage_header">
                    <h1>{pageHeader}</h1>
                    <h2>{patientDetails?.givenName + ' ' + patientDetails?.familyName}</h2>
                    <h4>NHS number: {patientDetails?.nhsNumber}</h4>
                    <div className="nhsuk-heading-xl" />
                    <h4>Preparing download for {numberOfFiles} files</h4>
                </div>
            </div>
            <h1 id="download-page-title">{pageHeader}</h1>

            {(submissionState === SUBMISSION_STATE.FAILED ||
                downloadState === SUBMISSION_STATE.FAILED) && <ServiceError />}

            {submissionState === SUBMISSION_STATE.PENDING && (
                <ProgressBar status="Loading..."></ProgressBar>
            )}

            {submissionState === SUBMISSION_STATE.SUCCEEDED && (
                <>
                    {searchResults.length && (
                        <>
                            <DocumentSearchResults searchResults={searchResults} />
                        </>
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
}

export default LloydGeorgeSelectDownloadStage;
