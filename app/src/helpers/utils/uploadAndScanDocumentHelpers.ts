import { Dispatch, SetStateAction } from 'react';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import { UploadSession } from '../../types/generic/uploadResult';
import { isRunningInCypress } from './isLocal';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { uploadDocumentToS3, virusScan } from '../requests/uploadDocuments';
import waitForSeconds from './waitForSeconds';
import { getLastURLPath } from './urlManipulations';

export const DELAY_BEFORE_VIRUS_SCAN_IN_SECONDS = isRunningInCypress() ? 0 : 3;
export const DELAY_BETWEEN_VIRUS_SCAN_RETRY_IN_SECONDS = isRunningInCypress() ? 0 : 5;

export const FREQUENCY_TO_UPDATE_DOCUMENT_STATE_DURING_UPLOAD = 2 * 60 * 1000; // 2 minutes

type UpdateDocumentArgs = {
    id: string;
    state: DOCUMENT_UPLOAD_STATE;
    progress?: number;
    attempts?: number;
    ref?: string;
};

export const setSingleDocument = (
    setDocuments: Dispatch<SetStateAction<UploadDocument[]>>,
    { id, state, progress, attempts, ref }: UpdateDocumentArgs,
) => {
    setDocuments((prevState) =>
        prevState.map((document) => {
            if (document.id === id) {
                progress = progress ?? document.progress;
                attempts = attempts ?? document.attempts;
                state = state ?? document.state;
                ref = ref ?? document.ref;

                return { ...document, state, progress, attempts };
            }
            return document;
        }),
    );
};
export const markDocumentsAsUploading = (
    documents: UploadDocument[],
    uploadSession: UploadSession,
) => {
    return documents.map((doc) => {
        const documentMetadata = uploadSession[doc.id];
        const documentReference = documentMetadata.fields.key;
        return {
            ...doc,
            state: DOCUMENT_UPLOAD_STATE.UPLOADING,
            key: documentReference,
            ref: getLastURLPath(documentReference),
        };
    });
};

type UploadAndScanSingleDocumentArgs = {
    setDocuments: Dispatch<SetStateAction<UploadDocument[]>>;
    document: UploadDocument;
    uploadSession: UploadSession;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

export async function uploadAndScanSingleDocument({
    document,
    uploadSession,
    setDocuments,
    baseUrl,
    baseHeaders,
}: UploadAndScanSingleDocumentArgs): Promise<void> {
    await uploadDocumentToS3({ setDocuments, document, uploadSession });
    setSingleDocument(setDocuments, {
        id: document.id,
        state: DOCUMENT_UPLOAD_STATE.SCANNING,
    });
    await waitForSeconds(DELAY_BEFORE_VIRUS_SCAN_IN_SECONDS);
    const virusDocumentState = await virusScan({
        documentReference: document.key ?? '',
        baseUrl,
        baseHeaders,
    });
    setSingleDocument(setDocuments, {
        id: document.id,
        state: virusDocumentState,
        progress: 100,
    });
}

export const getUploadMessage = ({ state, progress }: UploadDocument) => {
    const showProgress = state === DOCUMENT_UPLOAD_STATE.UPLOADING && progress !== undefined;

    if (state === DOCUMENT_UPLOAD_STATE.SELECTED) return 'Waiting...';
    else if (showProgress) return `${Math.round(progress)}% uploaded...`;
    else if (state === DOCUMENT_UPLOAD_STATE.FAILED) return 'Upload failed';
    else if (state === DOCUMENT_UPLOAD_STATE.INFECTED) return 'File has failed a virus scan';
    else if (state === DOCUMENT_UPLOAD_STATE.CLEAN) return 'Virus scan complete';
    else if (state === DOCUMENT_UPLOAD_STATE.SCANNING) return 'Virus scan in progress';
    else if (state === DOCUMENT_UPLOAD_STATE.SUCCEEDED) return 'Upload succeeded';
    else {
        return 'Upload failed';
    }
};
