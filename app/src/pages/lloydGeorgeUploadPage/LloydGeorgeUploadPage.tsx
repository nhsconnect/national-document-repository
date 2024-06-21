import React, { useEffect, useRef, useState } from 'react';
import LloydGeorgeUploadingStage from '../../components/blocks/_lloydGeorge/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import LloydGeorgeFileInputStage from '../../components/blocks/_lloydGeorge/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage';
import LloydGeorgeUploadInfectedStage from '../../components/blocks/_lloydGeorge/lloydGeorgeUploadInfectedStage/LloydGeorgeUploadInfectedStage';
import LloydGeorgeUploadCompleteStage from '../../components/blocks/_lloydGeorge/lloydGeorgeUploadCompleteStage/LloydGeorgeUploadCompleteStage';
import LloydGeorgeUploadFailedStage from '../../components/blocks/_lloydGeorge/lloydGeorgeUploadFailedStage/LloydGeorgeUploadFailedStage';
import { UploadSession } from '../../types/generic/uploadResult';
import uploadDocuments, {
    updateDocumentState,
    uploadConfirmation,
} from '../../helpers/requests/uploadDocuments';
import usePatient from '../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import { AxiosError } from 'axios';
import { isMock } from '../../helpers/utils/isLocal';
import Spinner from '../../components/generic/spinner/Spinner';
import { routeChildren, routes } from '../../types/generic/routes';
import { Outlet, Route, Routes, useNavigate } from 'react-router';
import { errorToParams } from '../../helpers/utils/errorToParams';
import LloydGeorgeRetryUploadStage from '../../components/blocks/_lloydGeorge/lloydGeorgeRetryUploadStage/LloydGeorgeRetryUploadStage';
import { getLastURLPath } from '../../helpers/utils/urlManipulations';
import {
    markDocumentsAsUploading,
    setSingleDocument,
    uploadAndScanSingleDocument,
} from '../../helpers/requests/uploadDocumentsHelper';

export enum LG_UPLOAD_STAGE {
    SELECT = 0,
    UPLOAD = 1,
    COMPLETE = 2,
    INFECTED = 3,
    FAILED = 4,
    CONFIRMATION = 5,
}

function LloydGeorgeUploadPage() {
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const [uploadSession, setUploadSession] = useState<UploadSession | null>(null);
    const confirmedReference = useRef(false);
    const exceededReference = useRef(false);
    const virusReference = useRef(false);
    const navigate = useNavigate();
    const [intervalTimer, setIntervalTimer] = useState(0);

    useEffect(() => {
        const hasExceededUploadAttempts = documents.some((d) => d.attempts > 1);
        const hasVirus = documents.some((d) => d.state === DOCUMENT_UPLOAD_STATE.INFECTED);
        const hasNoVirus =
            documents.length > 0 && documents.every((d) => d.state === DOCUMENT_UPLOAD_STATE.CLEAN);

        const handleUploadFailure = async () => {
            await updateDocumentState({
                documents: documents,
                uploadingState: false,
                baseUrl,
                baseHeaders,
            });
            navigate(routeChildren.LLOYD_GEORGE_UPLOAD_FAILED);
        };

        const confirmUpload = async () => {
            if (!uploadSession) {
                return;
            }
            navigate(routeChildren.LLOYD_GEORGE_UPLOAD_CONFIRMATION);
            try {
                const confirmDocumentState = await uploadConfirmation({
                    baseUrl,
                    baseHeaders,
                    nhsNumber,
                    uploadSession,
                    documents,
                });
                setDocuments((prevState) =>
                    prevState.map((document) => ({
                        ...document,
                        state: confirmDocumentState,
                    })),
                );
                window.clearInterval(intervalTimer);
                navigate(routeChildren.LLOYD_GEORGE_UPLOAD_COMPLETED);
            } catch (e) {
                const error = e as AxiosError;
                if (error.response?.status === 403) {
                    navigate(routes.SESSION_EXPIRED);
                    return;
                }
                void handleUploadFailure();
            }
        };

        if (hasExceededUploadAttempts && !exceededReference.current) {
            exceededReference.current = true;
            window.clearInterval(intervalTimer);
            void handleUploadFailure();
        } else if (hasVirus && !virusReference.current) {
            virusReference.current = true;
            window.clearInterval(intervalTimer);
            navigate(routeChildren.LLOYD_GEORGE_UPLOAD_INFECTED);
        } else if (hasNoVirus && !confirmedReference.current) {
            confirmedReference.current = true;
            void confirmUpload();
        }
    }, [
        baseHeaders,
        baseUrl,
        documents,
        navigate,
        nhsNumber,
        setDocuments,
        uploadSession,
        intervalTimer,
    ]);

    useEffect(() => {
        return () => {
            window.clearInterval(intervalTimer);
        };
    }, [intervalTimer]);

    const uploadAndScanSingleLloydGeorgeDocument = async (
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
            window.clearInterval(intervalTimer);
            markDocumentAsFailed(document);
        }
    };

    function markDocumentAsFailed(document: UploadDocument) {
        setSingleDocument(setDocuments, {
            id: document.id,
            state: DOCUMENT_UPLOAD_STATE.FAILED,
            attempts: document.attempts + 1,
            progress: 0,
        });
        void updateDocumentState({
            documents,
            uploadingState: false,
            baseUrl,
            baseHeaders,
        });
    }

    const uploadAndScanAllDocuments = (
        uploadDocuments: Array<UploadDocument>,
        uploadSession: UploadSession,
    ) => {
        uploadDocuments.forEach((document) => {
            void uploadAndScanSingleLloydGeorgeDocument(document, uploadSession);
        });
    };

    const submitDocuments = async () => {
        try {
            navigate(routeChildren.LLOYD_GEORGE_UPLOAD_UPLOADING);
            const uploadSession = await uploadDocuments({
                nhsNumber,
                documents,
                baseUrl,
                baseHeaders,
            });
            setUploadSession(uploadSession);
            const uploadingDocuments = markDocumentsAsUploading(documents, uploadSession);
            const updateStateInterval = startIntervalTimer(uploadingDocuments);
            setIntervalTimer(updateStateInterval);
            setDocuments(uploadingDocuments);
            uploadAndScanAllDocuments(uploadingDocuments, uploadSession);
            navigate(routeChildren.LLOYD_GEORGE_UPLOAD_UPLOADING);
        } catch (e) {
            const error = e as AxiosError;
            if (error.response?.status === 403) {
                navigate(routes.SESSION_EXPIRED);
            } else if (error.response?.status === 423) {
                navigate(routes.SERVER_ERROR + errorToParams(error));
            } else if (isMock(error)) {
                setDocuments((prevState) =>
                    prevState.map((doc) => ({
                        ...doc,
                        state: DOCUMENT_UPLOAD_STATE.SUCCEEDED,
                    })),
                );
                navigate(routeChildren.LLOYD_GEORGE_UPLOAD_COMPLETED);
            } else {
                setDocuments((prevState) =>
                    prevState.map((doc) => ({
                        ...doc,
                        state: DOCUMENT_UPLOAD_STATE.FAILED,
                        attempts: doc.attempts + 1,
                        progress: 0,
                    })),
                );
            }
        }
    };

    const restartUpload = () => {
        setDocuments([]);
        navigate(routes.LLOYD_GEORGE_UPLOAD);
    };

    const startIntervalTimer = (uploadDocuments: Array<UploadDocument>) => {
        return window.setInterval(() => {
            uploadDocuments.forEach(async (document) => {
                try {
                    await updateDocumentState({
                        documents,
                        uploadingState: true,
                        baseUrl,
                        baseHeaders,
                    });
                } catch (e) {}
            });
        }, 120000);
    };

    return (
        <>
            <div>
                <Routes>
                    <Route
                        index
                        element={
                            <LloydGeorgeFileInputStage
                                documents={documents}
                                setDocuments={setDocuments}
                                submitDocuments={submitDocuments}
                            />
                        }
                    />
                    <Route
                        path={getLastURLPath(routeChildren.LLOYD_GEORGE_UPLOAD_UPLOADING) + '/*'}
                        element={
                            <LloydGeorgeUploadingStage
                                documents={documents}
                                uploadSession={uploadSession}
                                uploadAndScanDocuments={uploadAndScanAllDocuments}
                            />
                        }
                    />
                    <Route
                        path={getLastURLPath(routeChildren.LLOYD_GEORGE_UPLOAD_CONFIRMATION) + '/*'}
                        element={<Spinner status="Checking uploads..." />}
                    />
                    <Route
                        path={getLastURLPath(routeChildren.LLOYD_GEORGE_UPLOAD_COMPLETED) + '/*'}
                        element={<LloydGeorgeUploadCompleteStage documents={documents} />}
                    />
                    <Route
                        path={getLastURLPath(routeChildren.LLOYD_GEORGE_UPLOAD_INFECTED) + '/*'}
                        element={
                            <LloydGeorgeUploadInfectedStage
                                documents={documents}
                                restartUpload={restartUpload}
                            />
                        }
                    />
                    <Route
                        path={getLastURLPath(routeChildren.LLOYD_GEORGE_UPLOAD_RETRY) + '/*'}
                        element={<LloydGeorgeRetryUploadStage />}
                    />
                    <Route
                        path={getLastURLPath(routeChildren.LLOYD_GEORGE_UPLOAD_FAILED) + '/*'}
                        element={<LloydGeorgeUploadFailedStage restartUpload={restartUpload} />}
                    />
                </Routes>

                <Outlet />
            </div>
        </>
    );
}

export default LloydGeorgeUploadPage;
