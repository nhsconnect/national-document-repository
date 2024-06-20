import { Dispatch, SetStateAction } from 'react';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import { UploadSession } from '../../types/generic/uploadResult';

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
export const addMetadataAndMarkDocumentAsUploading = (
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
const isRunningInCypress = () => {
    //@ts-ignore
    return Boolean(window?.Cypress);
};
export const DELAY_BEFORE_VIRUS_SCAN_IN_SECONDS = isRunningInCypress() ? 0 : 3;
