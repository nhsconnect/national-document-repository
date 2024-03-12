import { Dispatch, SetStateAction } from 'react';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import { S3Upload, S3UploadFields, UploadSession } from '../../types/generic/uploadResult';
import axios, { AxiosError } from 'axios';
import { setDocument } from './uploadDocuments';

type UploadDocumentsToS3Args = {
    setDocuments: Dispatch<SetStateAction<UploadDocument[]>>;
    documents: UploadDocument[];
    uploadSession: UploadSession;
};

const uploadDocumentsToS3 = async ({
    setDocuments,
    uploadSession,
    documents,
}: UploadDocumentsToS3Args) => {
    for (const document of documents) {
        try {
            const docGatewayResponse: S3Upload = uploadSession[document.file.name];
            const formData = new FormData();
            const docFields: S3UploadFields = docGatewayResponse.fields;
            Object.entries(docFields).forEach(([key, value]) => {
                formData.append(key, value);
            });
            formData.append('file', document.file);
            const s3url = docGatewayResponse.url;
            const s3Response = await axios.post(s3url, formData, {
                onUploadProgress: (progress) => {
                    const { loaded, total } = progress;
                    if (total) {
                        setDocument(setDocuments, {
                            id: document.id,
                            state: DOCUMENT_UPLOAD_STATE.UPLOADING,
                            progress: (loaded / total) * 100,
                        });
                    }
                },
            });

            const state =
                s3Response.status === 204
                    ? DOCUMENT_UPLOAD_STATE.SUCCEEDED
                    : DOCUMENT_UPLOAD_STATE.FAILED;
            setDocument(setDocuments, {
                id: document.id,
                state,
                attempts: 0,
                progress: 0,
            });
        } catch (e) {
            const error = e as AxiosError;

            const state =
                error.response?.status === 403
                    ? DOCUMENT_UPLOAD_STATE.UNAUTHORISED
                    : DOCUMENT_UPLOAD_STATE.FAILED;
            setDocument(setDocuments, {
                id: document.id,
                state,
                attempts: document.attempts + 1,
                progress: 0,
            });
        }
    }
};

export default uploadDocumentsToS3;
