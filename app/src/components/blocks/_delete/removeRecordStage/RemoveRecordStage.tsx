import React, { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import useTitle from '../../../../helpers/hooks/useTitle';
import { BackLink, Button, Table, WarningCallout } from 'nhsuk-react-components';
import PatientDetails from '../../../generic/patientDetails/PatientDetails';
import LinkButton from '../../../generic/linkButton/LinkButton';
import { SearchResult } from '../../../../types/generic/searchResult';
import getDocumentSearchResults from '../../../../helpers/requests/getDocumentSearchResults';
import usePatient from '../../../../helpers/hooks/usePatient';
import { SUBMISSION_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import { AxiosError } from 'axios';
import { Outlet, Route, Routes, useNavigate } from 'react-router';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import ServiceError from '../../../layout/serviceErrorBox/ServiceErrorBox';
import { getFormattedDatetime } from '../../../../helpers/utils/formatDatetime';
import ProgressBar from '../../../generic/progressBar/ProgressBar';
import { isMock } from '../../../../helpers/utils/isLocal';
import { buildSearchResult } from '../../../../helpers/test/testBuilders';
import { getLastURLPath } from '../../../../helpers/utils/urlManipulations';
import DeleteSubmitStage from '../deleteSubmitStage/DeleteSubmitStage';
import { DOCUMENT_TYPE } from '../../../../types/pages/UploadDocumentsPage/types';
import DeleteResultStage from '../deleteResultStage/DeleteResultStage';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';

export type Props = {
    numberOfFiles: number;
    recordType: string;
    setDownloadStage: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
};

function RemoveRecordStage({ numberOfFiles, recordType, setDownloadStage }: Props) {
    useTitle({ pageTitle: 'Remove record' });
    const patientDetails = usePatient();
    const [submissionState, setSubmissionState] = useState(SUBMISSION_STATE.PENDING);

    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const navigate = useNavigate();

    const [searchResults, setSearchResults] = useState<Array<SearchResult>>([]);

    const mounted = useRef(false);
    useEffect(() => {
        const onSuccess = (result: Array<SearchResult>) => {
            setSearchResults(result);
            setSubmissionState(SUBMISSION_STATE.SUCCEEDED);
        };

        const onPageLoad = async () => {
            try {
                const results = await getDocumentSearchResults({
                    nhsNumber,
                    baseUrl,
                    baseHeaders,
                });
                onSuccess(results ?? []);
            } catch (e) {
                const error = e as AxiosError;
                if (isMock(error)) {
                    onSuccess([buildSearchResult(), buildSearchResult()]);
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
        navigate,
        baseUrl,
        baseHeaders,
    ]);

    const hasDocuments = !!searchResults.length && !!patientDetails;

    const PageIndexView = () => (
        <>
            <BackLink
                data-testid="back-link"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    navigate(routes.LLOYD_GEORGE);
                }}
            >
                Go back
            </BackLink>
            <h1>Remove this {recordType}</h1>
            <WarningCallout>
                <WarningCallout.Label>Before removing</WarningCallout.Label>
                <p data-testid="remove-record-warning-text">
                    Only permanently remove this patient record if you have a valid reason to. For
                    example, you confirmed these files have reached the end of their{' '}
                    <a
                        href="https://transform.england.nhs.uk/information-governance/guidance/records-management-code/records-management-code-of-practice/#appendix-ii-retention-schedule"
                        target="_blank"
                        rel="noreferrer"
                    >
                        retention period
                    </a>
                    .
                </p>
            </WarningCallout>
            <PatientDetails />

            {submissionState === SUBMISSION_STATE.PENDING && <ProgressBar status="Loading..." />}

            {submissionState === SUBMISSION_STATE.FAILED && <ServiceError />}

            {submissionState === SUBMISSION_STATE.SUCCEEDED && (
                <>
                    {hasDocuments ? (
                        <>
                            <Table caption="List of files in record" id="current-documents-table">
                                <Table.Head>
                                    <Table.Row>
                                        <Table.Cell>Filename</Table.Cell>
                                        <Table.Cell>Upload date</Table.Cell>
                                    </Table.Row>
                                </Table.Head>

                                <Table.Body>
                                    {searchResults.map(({ fileName, created }: SearchResult) => {
                                        return (
                                            <Table.Row key={fileName}>
                                                <Table.Cell>
                                                    <div>{fileName}</div>
                                                </Table.Cell>
                                                <Table.Cell>
                                                    {getFormattedDatetime(new Date(created))}
                                                </Table.Cell>
                                            </Table.Row>
                                        );
                                    })}
                                </Table.Body>
                            </Table>
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
                <div className="align-bottom h-100">
                    {submissionState === SUBMISSION_STATE.SUCCEEDED && (
                        <Button
                            data-testid="remove-btn"
                            onClick={() => {
                                navigate(routeChildren.LLOYD_GEORGE_DELETE_CONFIRMATION);
                            }}
                        >
                            Remove all files
                        </Button>
                    )}
                    <LinkButton
                        id="start-again-link"
                        data-testid="start-again-btn"
                        type="button"
                        className="mb-7 ml-3"
                        onClick={() => {
                            navigate(routes.LLOYD_GEORGE);
                        }}
                    >
                        Start again
                    </LinkButton>
                </div>
            )}
        </>
    );

    return (
        <>
            <Routes>
                <Route index element={PageIndexView()}></Route>
                <Route
                    path={getLastURLPath(routeChildren.LLOYD_GEORGE_DELETE_CONFIRMATION)}
                    element={
                        <DeleteSubmitStage
                            docType={DOCUMENT_TYPE.LLOYD_GEORGE}
                            numberOfFiles={numberOfFiles}
                            recordType="Lloyd George"
                        />
                    }
                ></Route>
                <Route
                    path={getLastURLPath(routeChildren.ARF_DELETE_CONFIRMATION)}
                    element={
                        <DeleteSubmitStage
                            docType={DOCUMENT_TYPE.LLOYD_GEORGE}
                            numberOfFiles={numberOfFiles}
                            recordType="ARF"
                        />
                    }
                ></Route>
                <Route
                    path={getLastURLPath(routeChildren.LLOYD_GEORGE_DELETE_COMPLETE)}
                    element={
                        <DeleteResultStage
                            numberOfFiles={numberOfFiles}
                            setDownloadStage={setDownloadStage}
                        />
                    }
                ></Route>
            </Routes>
            <Outlet></Outlet>
        </>
    );
}
export default RemoveRecordStage;
