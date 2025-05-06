import { useEffect, useRef, useState } from 'react';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../types/pages/UploadDocumentsPage/types';
import { S3UploadFields, UploadSession } from '../../types/generic/uploadResult';
import uploadDocuments, {
    updateDocumentState,
    uploadConfirmation,
} from '../../helpers/requests/uploadDocuments';
import usePatient from '../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import { AxiosError } from 'axios';
import { isLocal, isMock } from '../../helpers/utils/isLocal';
import { routeChildren, routes } from '../../types/generic/routes';
import { Outlet, Route, Routes, useNavigate } from 'react-router-dom';
import { errorToParams } from '../../helpers/utils/errorToParams';
import { getLastURLPath } from '../../helpers/utils/urlManipulations';
import {
    FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD,
    markDocumentsAsUploading,
    setSingleDocument,
    uploadAndScanSingleDocument,
} from '../../helpers/utils/uploadAndScanDocumentHelpers';
import DocumentSelectStage from '../../components/blocks/_documentUpload/documentSelectStage/DocumentSelectStage';
import DocumentSelectOrderStage from '../../components/blocks/_documentUpload/documentSelectOrderStage/DocumentSelectOrderStage';
import DocumentUploadConfirmStage from '../../components/blocks/_documentUpload/documentUploadConfirmStage/DocumentUploadConfirmStage';
import DocumentUploadingStage from '../../components/blocks/_documentUpload/documentUploadingStage/DocumentUploadingStage';
import JSZip from 'jszip';
import { v4 as uuidv4 } from 'uuid';
import DocumentUploadCompleteStage from '../../components/blocks/_documentUpload/documentUploadCompleteStage/DocumentUploadCompleteStage';
import DocumentUploadRemoveFilesStage from '../../components/blocks/_documentUpload/documentUploadRemoveFilesStage/DocumentUploadRemoveFilesStage';

function DocumentUploadPage() {
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
    const [mergedPdfBlob, setMergedPdfBlob] = useState<Blob>();

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
                nhsNumber,
            });
            navigate(routeChildren.LLOYD_GEORGE_UPLOAD_FAILED);
        };

        const confirmUpload = async () => {
            if (!uploadSession) {
                return;
            }
            try {
                const confirmDocumentState = isLocal
                    ? DOCUMENT_UPLOAD_STATE.SUCCEEDED
                    : await uploadConfirmation({
                          baseUrl,
                          baseHeaders,
                          nhsNumber,
                          uploadSession,
                          documents,
                      });
                setDocuments((prevState) =>
                    isLocal
                        ? []
                        : prevState.map((document) => ({
                              ...document,
                              state: confirmDocumentState,
                          })),
                );
                window.clearInterval(intervalTimer);
                navigate(routeChildren.DOCUMENT_UPLOAD_COMPLETED);
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
        nhsNumber: string,
    ) => {
        try {
            await uploadAndScanSingleDocument({
                document,
                uploadSession,
                setDocuments,
                baseUrl,
                baseHeaders,
                nhsNumber,
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
            nhsNumber,
        });
    }

    const uploadAndScanAllDocuments = (
        uploadDocuments: Array<UploadDocument>,
        uploadSession: UploadSession,
        nhsNumber: string,
    ) => {
        uploadDocuments.forEach((document) => {
            void uploadAndScanSingleLloydGeorgeDocument(document, uploadSession, nhsNumber);
        });
    };

    const getMockUploadSession = (documents: UploadDocument[]): UploadSession => {
        const session: UploadSession = {};
        documents.forEach((doc) => {
            session[doc.id] = {
                url: 'https://example.com',
                fields: {
                    key: `https://example.com/${doc.id}`,
                } as S3UploadFields,
            };
        });

        return session;
    };

    const zipLloydGeorgeFiles = async (): Promise<Blob> => {
        const zipper = new JSZip();
        documents.forEach((doc) => {
            if (doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE) {
                zipper.file(doc.file.name, doc.file);
            }
        });
        return await zipper.generateAsync({
            type: 'blob',
            compression: 'DEFLATE',
            compressionOptions: { level: 6 },
        });
    };

    const submitDocuments = async () => {
        try {
            let reducedDocuments = documents;
            // if (reducedDocuments.some((doc) => doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE)) {
            //     const lloydGeorgeZip = await zipLloydGeorgeFiles();
            //     const lloydGeorgeZipFile = new File(
            //         [lloydGeorgeZip],
            //         `Compressed Lloyd George.zip`,
            //     );

            //     reducedDocuments = reducedDocuments.filter(
            //         (doc) => doc.docType !== DOCUMENT_TYPE.LLOYD_GEORGE,
            //     );
            //     reducedDocuments.push({
            //         id: uuidv4(),
            //         file: lloydGeorgeZipFile,
            //         state: DOCUMENT_UPLOAD_STATE.SELECTED,
            //         progress: 0,
            //         docType: DOCUMENT_TYPE.LLOYD_GEORGE,
            //         attempts: 0,
            //     });
            //     setDocuments(reducedDocuments);
            // }

            if (
                reducedDocuments.some((doc) => doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE) &&
                mergedPdfBlob
            ) {
                reducedDocuments = reducedDocuments.filter(
                    (doc) => doc.docType !== DOCUMENT_TYPE.LLOYD_GEORGE,
                );
                reducedDocuments.push({
                    id: uuidv4(),
                    file: new File(
                        [mergedPdfBlob],
                        `LloydGeorgeRecord_${patientDetails?.nhsNumber}.pdf`,
                    ),
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    progress: 0,
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    attempts: 0,
                });
            }

            const uploadSession: UploadSession = isLocal
                ? getMockUploadSession(reducedDocuments)
                : await uploadDocuments({
                      nhsNumber,
                      documents: reducedDocuments,
                      baseUrl,
                      baseHeaders,
                  });

            setUploadSession(uploadSession);
            const uploadingDocuments = markDocumentsAsUploading(reducedDocuments, uploadSession);
            const updateStateInterval = startIntervalTimer(uploadingDocuments);
            setIntervalTimer(updateStateInterval);
            setDocuments(uploadingDocuments);

            if (!isLocal) {
                uploadAndScanAllDocuments(uploadingDocuments, uploadSession, nhsNumber);
            }

            navigate(routeChildren.DOCUMENT_UPLOAD_UPLOADING);
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
                navigate(routeChildren.DOCUMENT_UPLOAD_COMPLETED);
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

    const startIntervalTimer = (uploadDocuments: Array<UploadDocument>) => {
        return window.setInterval(() => {
            if (isLocal) {
                const updatedDocuments = uploadDocuments.map((doc) => {
                    const min = (doc.progress ?? 0) + 10;
                    const max = 30;
                    doc.progress = Math.random() * (min + max - (min + 1)) + min;
                    if (doc.progress < 100) {
                        doc.state = DOCUMENT_UPLOAD_STATE.UPLOADING;
                    } else if (doc.state !== DOCUMENT_UPLOAD_STATE.SCANNING) {
                        doc.state = DOCUMENT_UPLOAD_STATE.SCANNING;
                    } else {
                        doc.state = DOCUMENT_UPLOAD_STATE.CLEAN;
                    }
                    return doc;
                });
                setDocuments(updatedDocuments);
            } else {
                void updateDocumentState({
                    documents: uploadDocuments,
                    uploadingState: true,
                    baseUrl,
                    baseHeaders,
                    nhsNumber,
                });
            }
        }, FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD);
    };

    return (
        <>
            <div>
                <Routes>
                    <Route
                        index
                        element={
                            <DocumentSelectStage
                                documents={documents}
                                setDocuments={setDocuments}
                                documentType={DOCUMENT_TYPE.LLOYD_GEORGE}
                            />
                        }
                    />
                    <Route
                        path={getLastURLPath(routeChildren.DOCUMENT_UPLOAD_SELECT_ORDER) + '/*'}
                        element={
                            <DocumentSelectOrderStage
                                documents={documents}
                                setDocuments={setDocuments}
                                setMergedPdfBlob={setMergedPdfBlob}
                            />
                        }
                    />
                    <Route
                        path={getLastURLPath(routeChildren.DOCUMENT_UPLOAD_REMOVE_ALL) + '/*'}
                        element={
                            <DocumentUploadRemoveFilesStage
                                documents={documents}
                                setDocuments={setDocuments}
                                documentType={DOCUMENT_TYPE.LLOYD_GEORGE}
                            />
                        }
                    />
                    <Route
                        path={getLastURLPath(routeChildren.DOCUMENT_UPLOAD_CONFIRMATION) + '/*'}
                        element={
                            <DocumentUploadConfirmStage
                                documents={documents}
                                startUpload={submitDocuments}
                            />
                        }
                    />
                    <Route
                        path={getLastURLPath(routeChildren.DOCUMENT_UPLOAD_UPLOADING) + '/*'}
                        element={<DocumentUploadingStage documents={documents} />}
                    />
                    <Route
                        path={getLastURLPath(routeChildren.DOCUMENT_UPLOAD_COMPLETED) + '/*'}
                        element={<DocumentUploadCompleteStage />}
                    />
                </Routes>

                <Outlet />
            </div>
        </>
    );
}

export default DocumentUploadPage;
