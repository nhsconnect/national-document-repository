import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import axios, { AxiosError } from 'axios';
import { S3Upload, S3UploadFields, UploadResult } from '../../types/generic/uploadResult';
import { Dispatch, SetStateAction } from 'react';

type UploadDocumentsArgs = {
    setDocuments: Dispatch<SetStateAction<UploadDocument[]>>;
    documents: UploadDocument[];
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type UploadDocumentsToS3Args = {
    setDocument: (props: DocumentStateProps) => void;
    documents: UploadDocument[];
    data: UploadResult;
};

type gatewayResponse = {
    data: UploadResult;
};

type DocumentStateProps = {
    id: string;
    state: DOCUMENT_UPLOAD_STATE;
    progress?: number;
    attempts?: number;
};

const uploadDocument = async ({
    nhsNumber,
    setDocuments,
    documents,
    baseUrl,
    baseHeaders,
}: UploadDocumentsArgs) => {
    /**
     * Upload Document helpers
     */
    const setDocument = ({ id, state, progress, attempts }: DocumentStateProps) => {
        const newDocumentsState = documents.map((document) => {
            if (document.id === id) {
                progress = progress ?? document.progress;
                attempts = attempts ?? document.attempts;
                return { ...document, state, progress, attempts };
            }
            return document;
        });
        setDocuments(newDocumentsState);
    };
    const docDetails = (document: UploadDocument) => {
        setDocument({ id: document.id, state: DOCUMENT_UPLOAD_STATE.UPLOADING });
        return {
            fileName: document.file.name,
            contentType: document.file.type,
            docType: document.docType,
        };
    };
    const uploadDocumentsToS3 = async ({
        setDocument,
        documents,
        data,
    }: UploadDocumentsToS3Args) => {
        for (const document of documents) {
            try {
                const docGatewayResponse: S3Upload = data[document.file.name];
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
                            setDocument({
                                id: document.id,
                                state: DOCUMENT_UPLOAD_STATE.UPLOADING,
                                progress: (loaded / total) * 100,
                            });
                        }
                    },
                });

                const state =
                    s3Response.status === 403
                        ? DOCUMENT_UPLOAD_STATE.UNAUTHORISED
                        : DOCUMENT_UPLOAD_STATE.FAILED;
                setDocument({
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
                setDocument({
                    id: document.id,
                    state,
                    attempts: document.attempts + 1,
                    progress: 0,
                });
            }
        }
    };

    /**
     * Upload Document request
     */
    const requestBody = {
        resourceType: 'DocumentReference',
        subject: {
            identifier: {
                system: 'https://fhir.nhs.uk/Id/nhs-number',
                value: nhsNumber,
            },
        },
        type: {
            coding: [
                {
                    system: 'http://snomed.info/sct',
                    code: '22151000087106',
                },
            ],
        },
        content: [
            {
                attachment: documents.map(docDetails),
            },
        ],
        created: new Date(Date.now()).toISOString(),
    };

    const gatewayUrl = baseUrl + endpoints.DOCUMENT_UPLOAD;

    try {
        const { data }: gatewayResponse = await axios.post(
            gatewayUrl,
            JSON.stringify(requestBody),
            {
                headers: {
                    ...baseHeaders,
                },
            },
        );
        await uploadDocumentsToS3({ setDocument, documents, data });
    } catch (e) {
        const error = e as AxiosError;

        const state =
            error.response?.status === 403
                ? DOCUMENT_UPLOAD_STATE.UNAUTHORISED
                : DOCUMENT_UPLOAD_STATE.FAILED;

        const failedDocuments = documents.map((doc) => ({
            ...doc,
            state,
            attempts: doc.attempts + 1,
            progress: 0,
        }));
        setDocuments(failedDocuments);
    }
};

export default uploadDocument;
