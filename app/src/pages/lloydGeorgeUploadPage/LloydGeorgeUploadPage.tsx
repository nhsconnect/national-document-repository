import React, { useEffect, useState } from 'react';
import LloydGeorgeUploadingStage from '../../components/blocks/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import LloydGeorgeFileInputStage from '../../components/blocks/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage';
import LloydGeorgeUploadFailure from '../../components/blocks/lloydGeorgeUploadFailure/LloydGeorgeUploadFailure';
import LloydGeorgeUploadCompleteStage from '../../components/blocks/lloydGeorgeUploadCompleteStage/LloydGeorgeUploadCompleteStage';
import LloydGeorgeRetryUploadStage from '../../components/blocks/lloydGeorgeRetryUploadStage/LloydGeorgeRetryUploadStage';
import { UploadSession } from '../../types/generic/uploadResult';
import uploadDocuments, {
    setDocument,
    uploadConfirmation,
    uploadDocumentToS3,
    virusScanResult,
} from '../../helpers/requests/uploadDocuments';
import usePatient from '../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import { AxiosError } from 'axios';
import { isMock } from '../../helpers/utils/isLocal';

export enum LG_UPLOAD_STAGE {
    SELECT = 0,
    UPLOAD = 1,
    COMPLETE = 2,
    INFECTED = 3,
    RETRY = 4,
    CONFIRMATION = 5,
}

function LloydGeorgeUploadPage() {
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const [stage, setStage] = useState<LG_UPLOAD_STAGE>(LG_UPLOAD_STAGE.SELECT);
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const [uploadSession, setUploadSession] = useState<UploadSession | null>(null);

    useEffect(() => {
        const hasExceededUploadAttempts = documents.some((d) => d.attempts > 1);
        const hasVirus = documents.some((d) => d.state === DOCUMENT_UPLOAD_STATE.INFECTED);
        const hasNoVirus = documents.every((d) => d.state === DOCUMENT_UPLOAD_STATE.CLEAN);

        const confirmUpload = async () => {
            if (uploadSession) {
                setStage(LG_UPLOAD_STAGE.CONFIRMATION);
                await uploadConfirmation({
                    baseUrl,
                    baseHeaders,
                    nhsNumber,
                    uploadSession,
                    documents,
                });
                setDocuments(
                    documents.map((document) => ({
                        ...document,
                        state: DOCUMENT_UPLOAD_STATE.SUCCEEDED,
                    })),
                );
                setStage(LG_UPLOAD_STAGE.COMPLETE);
            }
        };

        if (hasExceededUploadAttempts) {
            setDocuments([]);
            setStage(LG_UPLOAD_STAGE.RETRY);
        } else if (hasVirus) {
            setStage(LG_UPLOAD_STAGE.INFECTED);
        } else if (hasNoVirus) {
            confirmUpload();
        }
    }, [baseHeaders, baseUrl, documents, nhsNumber, setDocuments, setStage, uploadSession]);

    const uploadAndScanDocuments = (
        documents: Array<UploadDocument>,
        uploadSession: UploadSession,
    ) => {
        documents.forEach(async (document) => {
            const documentMetadata = uploadSession[document.file.name];
            const documentReference = documentMetadata.fields.key;
            await uploadDocumentToS3({ setDocuments, document, uploadSession });
            setDocument(setDocuments, {
                id: document.id,
                state: DOCUMENT_UPLOAD_STATE.SCANNING,
                progress: 'scan',
            });
            const virusDocumentState = await virusScanResult({
                documentReference,
                baseUrl,
                baseHeaders,
            });
            setDocument(setDocuments, {
                id: document.id,
                state: virusDocumentState,
                progress: 100,
            });
        });
    };

    const submitDocuments = async () => {
        try {
            setStage(LG_UPLOAD_STAGE.UPLOAD);
            const uploadSession = await uploadDocuments({
                nhsNumber,
                setDocuments,
                documents,
                baseUrl,
                baseHeaders,
            });
            setUploadSession(uploadSession);
            uploadAndScanDocuments(documents, uploadSession);
        } catch (e) {
            const error = e as AxiosError;
            if (isMock(error)) {
                setDocuments(
                    documents.map((document) => ({
                        ...document,
                        state: DOCUMENT_UPLOAD_STATE.SUCCEEDED,
                    })),
                );
                setStage(LG_UPLOAD_STAGE.COMPLETE);
            }
        }
    };

    switch (stage) {
        case LG_UPLOAD_STAGE.SELECT:
            return (
                <LloydGeorgeFileInputStage
                    documents={documents}
                    setDocuments={setDocuments}
                    submitDocuments={submitDocuments}
                />
            );
        case LG_UPLOAD_STAGE.UPLOAD:
            return (
                <LloydGeorgeUploadingStage
                    documents={documents}
                    uploadSession={uploadSession}
                    uploadAndScanDocuments={uploadAndScanDocuments}
                />
            );
        case LG_UPLOAD_STAGE.COMPLETE:
            return <LloydGeorgeUploadCompleteStage documents={documents} />;
        case LG_UPLOAD_STAGE.INFECTED:
            return <LloydGeorgeUploadFailure documents={documents} setStage={setStage} />;
        case LG_UPLOAD_STAGE.RETRY:
            return <LloydGeorgeRetryUploadStage setStage={setStage} />;
        case LG_UPLOAD_STAGE.CONFIRMATION:
            return <div>CONFIRMING</div>;
        default:
            return <div />;
    }
}

export default LloydGeorgeUploadPage;
