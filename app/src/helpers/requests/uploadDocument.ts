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
    setDocumentState: (id: string, state: DOCUMENT_UPLOAD_STATE, progress?: number) => void;
    documents: UploadDocument[];
    data: UploadResult;
    baseUrl: string;
};

type gatewayResponse = {
    data: UploadResult;
};

const uploadDocument = async ({
    nhsNumber,
    setDocuments,
    documents,
    baseUrl,
    baseHeaders,
}: UploadDocumentsArgs) => {
    const setDocumentState = (id: string, state: DOCUMENT_UPLOAD_STATE, progress?: number) => {
        setDocuments((prevDocuments: UploadDocument[]) => {
            return prevDocuments.map((document) => {
                if (document.id === id) {
                    progress = progress ?? document.progress;
                    return { ...document, state, progress };
                }
                return document;
            });
        });
    };
    const docDetails = (document: UploadDocument) => {
        setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.UPLOADING);
        return {
            fileName: document.file.name,
            contentType: document.file.type,
            docType: document.docType,
        };
    };
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

    const uploadGatewayUrl = baseUrl + endpoints.DOCUMENT_UPLOAD;

    try {
        const { data }: gatewayResponse = await axios.post(
            uploadGatewayUrl,
            JSON.stringify(requestBody),
            {
                headers: {
                    ...baseHeaders,
                },
            },
        );
        await uploadDocumentsToS3({ setDocumentState, documents, data, baseUrl });
    } catch (e) {
        const error = e as AxiosError;
        if (error.response?.status === 403) {
            documents.forEach((document) => {
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.UNAUTHORISED);
            });
            throw e;
        } else {
            documents.forEach((document) => {
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.FAILED);
            });
            throw e;
        }
    }
};

const uploadDocumentsToS3 = async ({
    setDocumentState,
    documents,
    data,
    baseUrl,
}: UploadDocumentsToS3Args) => {
    const virusScanGatewayUrl = baseUrl + endpoints.VIRUS_SCAN;

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
                        setDocumentState(
                            document.id,
                            DOCUMENT_UPLOAD_STATE.UPLOADING,
                            (loaded / total) * 100,
                        );
                    }
                },
            });
            const requestBody = {
                documentReference: docGatewayResponse.fields.key,
            };
            if (s3Response.status === 204) {
                try {
                    setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.SCANNING, undefined);
                    await axios.post(virusScanGatewayUrl, requestBody);
                } catch (e) {
                    const error = e as AxiosError;
                    if (error.response?.status === 400) {
                        setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.INFECTED);
                    }
                    throw e;
                }
            }
            setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.SUCCEEDED, 100);
        } catch (e) {
            const error = e as AxiosError;
            if (error.response?.status === 403) {
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.UNAUTHORISED);
            } else if (document.state === DOCUMENT_UPLOAD_STATE.INFECTED) {
                throw e;
            } else {
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.FAILED);
                throw e;
            }
        }
    }
};

export default uploadDocument;
