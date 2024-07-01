import React, { useEffect, useRef, useState } from 'react';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import SelectStage from '../../components/blocks/_arf/selectStage/SelectStage';
import UploadingStage from '../../components/blocks/_arf/uploadingStage/UploadingStage';
import CompleteStage from '../../components/blocks/_arf/completeStage/CompleteStage';
import { routeChildren, routes } from '../../types/generic/routes';
import { NavigateFunction, Outlet, Route, Routes, useNavigate } from 'react-router';
import useConfig from '../../helpers/hooks/useConfig';
import { getLastURLPath } from '../../helpers/utils/urlManipulations';
import { useLocation } from 'react-router-dom';
import Spinner from '../../components/generic/spinner/Spinner';
import {
    markDocumentsAsUploading,
    setSingleDocument,
    FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD,
    uploadAndScanSingleDocument,
} from '../../helpers/utils/uploadAndScanDocumentHelpers';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import uploadDocuments, {
    updateDocumentState,
    uploadConfirmation,
} from '../../helpers/requests/uploadDocuments';
import { AxiosError } from 'axios';
import { UploadSession } from '../../types/generic/uploadResult';
import { isMock } from '../../helpers/utils/isLocal';
import { errorToParams } from '../../helpers/utils/errorToParams';
import usePatient from '../../helpers/hooks/usePatient';
import { buildUploadSession } from '../../helpers/test/testBuilders';

function UploadDocumentsPage() {
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const [uploadSession, setUploadSession] = useState<UploadSession | null>(null);
    const [intervalTimer, setIntervalTimer] = useState(0);

    const config = useConfig();
    const navigate = useNavigate();
    const location = useLocation();
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';

    const mounted = useRef(false);

    const isUploading = location.pathname === routeChildren.ARF_UPLOAD_UPLOADING;

    const startIntervalTimer = (uploadDocuments: Array<UploadDocument>): number => {
        const setAllDocumentStatesToUploading = () => {
            void updateDocumentState({
                documents: uploadDocuments,
                uploadingState: true,
                baseUrl,
                baseHeaders,
            });
        };

        return window.setInterval(
            setAllDocumentStatesToUploading,
            FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD,
        );
    };

    useEffect(() => {
        const onPageLoad = () => {
            if (
                !config.featureFlags.uploadArfWorkflowEnabled ||
                !config.featureFlags.uploadLambdaEnabled
            ) {
                navigate(routes.UNAUTHORISED);
            }
        };

        if (!mounted.current) {
            mounted.current = true;
            onPageLoad();
        }
    }, [navigate, config]);

    useEffect(() => {
        return () => {
            window.clearInterval(intervalTimer);
        };
    }, [intervalTimer]);

    useEffect(() => {
        if (!isUploading || !uploadSession) {
            return;
        }

        const allDocumentsFinishedVirusScan =
            documents.length > 0 &&
            documents.every((document) => {
                return [
                    DOCUMENT_UPLOAD_STATE.CLEAN,
                    DOCUMENT_UPLOAD_STATE.INFECTED,
                    DOCUMENT_UPLOAD_STATE.FAILED,
                ].includes(document.state);
            });

        if (!allDocumentsFinishedVirusScan) {
            return;
        }

        const confirmUpload = async (cleanDocuments: UploadDocument[]) => {
            try {
                const confirmDocumentState = await uploadConfirmation({
                    baseUrl,
                    baseHeaders,
                    nhsNumber,
                    uploadSession,
                    documents: cleanDocuments,
                });

                cleanDocuments.forEach((doc) =>
                    setSingleDocument(setDocuments, {
                        id: doc.id,
                        state: confirmDocumentState,
                    }),
                );

                navigate(routeChildren.ARF_UPLOAD_COMPLETED);
            } catch (error) {
                handleUploadConfirmationError(error as AxiosError);
            }
        };

        const handleUploadConfirmationError = (error: AxiosError) => {
            if (error.response?.status === 403) {
                navigate(routes.SESSION_EXPIRED);
            } else if (isMock(error)) {
                mockUploadConfirmationSucceed(setDocuments, navigate);
            } else {
                navigate(routes.SERVER_ERROR + errorToParams(error));
            }
        };

        window.clearInterval(intervalTimer);

        const cleanDocuments = documents.filter(
            (document) => document.state === DOCUMENT_UPLOAD_STATE.CLEAN,
        );
        if (cleanDocuments.length > 0) {
            navigate(routeChildren.ARF_UPLOAD_CONFIRMATION);
            void confirmUpload(cleanDocuments);
        } else {
            navigate(routeChildren.ARF_UPLOAD_FAILED);
            void updateDocumentState({
                documents,
                baseUrl,
                baseHeaders,
                uploadingState: false,
            });
        }
    }, [
        isUploading,
        documents,
        uploadSession,
        intervalTimer,
        navigate,
        baseUrl,
        baseHeaders,
        nhsNumber,
    ]);

    const startUpload = async () => {
        let timerId;
        try {
            navigate(routeChildren.ARF_UPLOAD_UPLOADING);

            const uploadSession = await uploadDocuments({
                nhsNumber,
                documents,
                baseUrl,
                baseHeaders,
            });
            setUploadSession(uploadSession);
            const uploadingDocuments: UploadDocument[] = markDocumentsAsUploading(
                documents,
                uploadSession,
            );
            setDocuments(uploadingDocuments);

            timerId = startIntervalTimer(uploadingDocuments);
            setIntervalTimer(timerId);

            uploadingDocuments.forEach((document) => {
                void uploadAndScanSingleArfDocument(document, uploadSession);
            });
        } catch (error) {
            window.clearInterval(timerId);
            handleUploadError(error as AxiosError);
        }
    };

    const uploadAndScanSingleArfDocument = async (
        document: UploadDocument,
        uploadSession: UploadSession,
    ) => {
        try {
            await uploadAndScanSingleDocument({
                document,
                uploadSession,
                setDocuments,
                baseUrl,
                baseHeaders,
            });
        } catch (e) {
            markDocumentAsFailed(document);
        }
    };

    const handleUploadError = (error: AxiosError) => {
        if (error.response?.status === 403) {
            navigate(routes.SESSION_EXPIRED);
        } else if (isMock(error)) {
            mockVirusScanClean(documents, setDocuments, setUploadSession);
        } else {
            navigate(routes.SERVER_ERROR + errorToParams(error));
        }
    };

    const markDocumentAsFailed = (failedDocument: UploadDocument) => {
        setSingleDocument(setDocuments, {
            id: failedDocument.id,
            state: DOCUMENT_UPLOAD_STATE.FAILED,
            progress: 0,
        });
    };

    return (
        <>
            <Routes>
                <Route
                    index
                    element={
                        <SelectStage
                            setDocuments={setDocuments}
                            documents={documents}
                            startUpload={startUpload}
                        />
                    }
                ></Route>
                <Route
                    path={getLastURLPath(routeChildren.ARF_UPLOAD_UPLOADING)}
                    element={<UploadingStage documents={documents} />}
                ></Route>
                <Route
                    path={getLastURLPath(routeChildren.ARF_UPLOAD_CONFIRMATION)}
                    element={
                        <div>
                            <Spinner status="Checking uploads..." />
                        </div>
                    }
                ></Route>
                <Route
                    path={getLastURLPath(routeChildren.ARF_UPLOAD_COMPLETED)}
                    element={<CompleteStage documents={documents} />}
                ></Route>
                <Route
                    path={getLastURLPath(routeChildren.ARF_UPLOAD_FAILED)}
                    element={
                        <div>
                            <h1>All files failed to upload</h1>
                            <p>
                                The electronic health record was not uploaded for this patient. You
                                will need to check your files and try again.
                            </p>
                            <p>
                                Make sure to safely store the electronic health record until it's
                                completely uploaded to this storage.
                            </p>
                        </div>
                    }
                ></Route>
            </Routes>
            <Outlet></Outlet>
        </>
    );
}

/* istanbul ignore next */
function mockUploadConfirmationSucceed(
    setDocuments: React.Dispatch<React.SetStateAction<UploadDocument[]>>,
    navigate: NavigateFunction,
) {
    setDocuments((prevState) =>
        prevState.map((doc) => ({
            ...doc,
            state: DOCUMENT_UPLOAD_STATE.SUCCEEDED,
        })),
    );
    navigate(routeChildren.ARF_UPLOAD_COMPLETED);
}

/* istanbul ignore next */
function mockVirusScanClean(
    documents: Array<UploadDocument>,
    setDocuments: React.Dispatch<React.SetStateAction<UploadDocument[]>>,
    setUploadSession: React.Dispatch<React.SetStateAction<UploadSession | null>>,
) {
    setUploadSession(buildUploadSession(documents));
    setDocuments((prevState) =>
        prevState.map((doc) => ({
            ...doc,
            state: DOCUMENT_UPLOAD_STATE.CLEAN,
            progress: 100,
        })),
    );
}

export default UploadDocumentsPage;
