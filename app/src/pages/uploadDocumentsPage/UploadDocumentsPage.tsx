import React, { useEffect, useRef, useState } from 'react';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import SelectStage from '../../components/blocks/_arf/selectStage/SelectStage';
import UploadingStage from '../../components/blocks/_arf/uploadingStage/UploadingStage';
import CompleteStage from '../../components/blocks/_arf/completeStage/CompleteStage';
import { routeChildren, routes } from '../../types/generic/routes';
import { Outlet, Route, Routes, useNavigate } from 'react-router';
import useConfig from '../../helpers/hooks/useConfig';
import { getLastURLPath } from '../../helpers/utils/urlManipulations';
import { useLocation } from 'react-router-dom';
import Spinner from '../../components/generic/spinner/Spinner';
import {
    markDocumentsAsUploading,
    setSingleDocument,
    uploadAndScanSingleDocument,
} from '../../helpers/utils/uploadAndScanDocumentHelpers';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import uploadDocuments from '../../helpers/requests/uploadDocuments';
import { AxiosError } from 'axios';
import { UploadSession } from '../../types/generic/uploadResult';
import { isMock } from '../../helpers/utils/isLocal';
import { errorToParams } from '../../helpers/utils/errorToParams';
import usePatient from '../../helpers/hooks/usePatient';

function UploadDocumentsPage() {
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const config = useConfig();
    const navigate = useNavigate();
    const location = useLocation();
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';

    const mounted = useRef(false);

    const isUploading = location.pathname === routeChildren.ARF_UPLOAD_UPLOADING;
    const someDocumentsAreClean = documents.some(
        (document) => document.state === DOCUMENT_UPLOAD_STATE.CLEAN,
    );

    const allDocumentsFinishedVirusScan =
        documents.length > 0 &&
        documents.every((document) =>
            [
                DOCUMENT_UPLOAD_STATE.CLEAN,
                DOCUMENT_UPLOAD_STATE.INFECTED,
                DOCUMENT_UPLOAD_STATE.FAILED,
            ].includes(document.state),
        );

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
        const confirmUpload = async () => {
            navigate(routeChildren.ARF_UPLOAD_CONFIRMATION);
            const documentsToConfirm = documents.filter(
                (doc) => doc.state === DOCUMENT_UPLOAD_STATE.CLEAN,
            );
            // eslint-disable-next-line no-console
            console.log('calling confirm upload API here...');
            documentsToConfirm.forEach((doc) =>
                setSingleDocument(setDocuments, {
                    id: doc.id,
                    state: DOCUMENT_UPLOAD_STATE.SUCCEEDED,
                }),
            );

            navigate(routeChildren.ARF_UPLOAD_COMPLETED);
        };

        if (!isUploading) {
            return;
        }
        if (allDocumentsFinishedVirusScan) {
            if (someDocumentsAreClean) {
                void confirmUpload();
            } else {
                navigate(routeChildren.ARF_UPLOAD_FAILED);
            }
        }
    }, [documents, isUploading, someDocumentsAreClean, allDocumentsFinishedVirusScan, navigate]);

    const startUpload = async () => {
        try {
            const uploadSession = await uploadDocuments({
                nhsNumber,
                documents,
                baseUrl,
                baseHeaders,
            });
            const uploadingDocuments: UploadDocument[] = markDocumentsAsUploading(
                documents,
                uploadSession,
            );
            setDocuments(uploadingDocuments);

            uploadingDocuments.forEach((document) => {
                void uploadAndScanSingleArfDocument(document, uploadSession);
            });
        } catch (error) {
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
            /* istanbul ignore next */
            setDocuments((prevState) =>
                prevState.map((doc) => ({
                    ...doc,
                    state: DOCUMENT_UPLOAD_STATE.CLEAN,
                })),
            );
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
                    path={getLastURLPath(routeChildren.ARF_UPLOAD_COMPLETED)}
                    element={<CompleteStage documents={documents} />}
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
                    path={getLastURLPath(routeChildren.ARF_UPLOAD_FAILED)}
                    element={
                        <div>
                            <h1>Failed to upload documents</h1>
                        </div>
                    }
                ></Route>
            </Routes>
            <Outlet></Outlet>
        </>
    );
}

export default UploadDocumentsPage;
