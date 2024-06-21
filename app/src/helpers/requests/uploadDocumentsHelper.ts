import { Dispatch, SetStateAction } from 'react';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import { UploadSession } from '../../types/generic/uploadResult';
import { isRunningInCypress } from '../utils/isLocal';
import { AuthHeaders } from '../../types/blocks/authHeaders';
import { uploadDocumentToS3, virusScanResult } from './uploadDocuments';
import waitForSeconds from '../utils/waitForSeconds';

export const DELAY_BEFORE_VIRUS_SCAN_IN_SECONDS = isRunningInCypress() ? 0 : 3;
export const DELAY_BETWEEN_VIRUS_SCAN_RETRY_IN_SECONDS = isRunningInCypress() ? 0 : 5;

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
        const documentMetadata = uploadSession[doc.file.name];
        const documentReference = documentMetadata.fields.key;
        return {
            ...doc,
            state: DOCUMENT_UPLOAD_STATE.UPLOADING,
            key: documentReference,
            ref: documentReference.split('/').at(-1),
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
    const virusDocumentState = await virusScanResult({
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
