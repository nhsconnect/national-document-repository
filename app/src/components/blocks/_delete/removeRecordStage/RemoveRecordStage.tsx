import React, { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
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
import { useNavigate } from 'react-router';
import { routes } from '../../../../types/generic/routes';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import ServiceError from '../../../layout/serviceErrorBox/ServiceErrorBox';
import { getFormattedDatetime } from '../../../../helpers/utils/formatDatetime';
import ProgressBar from '../../../generic/progressBar/ProgressBar';
import { isMock } from '../../../../helpers/utils/isLocal';
import { buildSearchResult } from '../../../../helpers/test/testBuilders';

export type Props = {
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    recordType: string;
};

function RemoveRecordStage({ setStage, recordType }: Props) {
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

    return (
        <>
            <BackLink
                data-testid="back-link"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    setStage(LG_RECORD_STAGE.RECORD);
                }}
            >
                Go back
            </BackLink>
            <h1>Remove this {recordType}</h1>
            <WarningCallout>
                <WarningCallout.Label>Before removing</WarningCallout.Label>
                <p>
                    Only permanently remove this patient record if you have a valid reason to. For
                    example, you confirmed these files have reached the end of their retention
                    period.
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
                            onClick={() => {
                                setStage(LG_RECORD_STAGE.DELETE_ALL);
                            }}
                        >
                            Remove all files
                        </Button>
                    )}
                    <LinkButton
                        id="start-again-link"
                        type="button"
                        className="mb-7 ml-3"
                        onClick={() => {
                            setStage(LG_RECORD_STAGE.RECORD);
                        }}
                    >
                        Start again
                    </LinkButton>
                </div>
            )}
        </>
    );
}
export default RemoveRecordStage;
