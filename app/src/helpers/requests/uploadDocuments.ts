import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../types/pages/UploadDocumentsPage/types';

import axios, { AxiosError } from 'axios';
import { S3Upload, S3UploadFields, UploadSession } from '../../types/generic/uploadResult';
import { Dispatch, SetStateAction } from 'react';
import { setDocument } from '../../pages/lloydGeorgeUploadPage/LloydGeorgeUploadPage';

type FileKeyBuilder = {
    [key in DOCUMENT_TYPE]: string[];
};

type UploadDocumentsArgs = {
    documents: UploadDocument[];
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type UploadDocumentsToS3Args = {
    setDocuments: Dispatch<SetStateAction<UploadDocument[]>>;
    document: UploadDocument;
    uploadSession: UploadSession;
};

type DocRefResponse = {
    data: UploadSession;
};

type VirusScanArgs = {
    documentReference: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};
type UploadConfirmationArgs = {
    baseUrl: string;
    baseHeaders: AuthHeaders;
    nhsNumber: string;
    documents: Array<UploadDocument>;
    uploadSession: UploadSession;
};

type UpdateUploadDocumentStateArgs = {
    uploading: boolean;
    documents: Array<UploadDocument>;
    baseUrl: string;
    baseHeaders: AuthHeaders;
    uploadSession: UploadSession;
};

export const virusScanResult = async ({
    documentReference,
    baseUrl,
    baseHeaders,
}: VirusScanArgs) => {
    const virusScanGatewayUrl = baseUrl + endpoints.VIRUS_SCAN;
    const body = { documentReference };
    try {
        await axios.post(virusScanGatewayUrl, body, {
            headers: {
                ...baseHeaders,
            },
        });
        return DOCUMENT_UPLOAD_STATE.CLEAN;
    } catch (e) {
        return DOCUMENT_UPLOAD_STATE.INFECTED;
    }
};

export const uploadConfirmation = async ({
    baseUrl,
    baseHeaders,
    nhsNumber,
    documents,
    uploadSession,
}: UploadConfirmationArgs) => {
    const fileKeyBuilder = documents.reduce((acc, doc) => {
        const documentMetadata = uploadSession[doc.file.name];
        const fileKey = documentMetadata.fields.key.split('/');
        const previousKeys = acc[doc.docType] ?? [];

        return {
            ...acc,
            [doc.docType]: [...previousKeys, fileKey[3]],
        };
    }, {} as FileKeyBuilder);

    const uploadConfirmationGatewayUrl = baseUrl + endpoints.UPLOAD_CONFIRMATION;
    const confirmationBody = {
        patientId: nhsNumber,
        documents: { ...fileKeyBuilder },
    };
    try {
        await axios.post(uploadConfirmationGatewayUrl, confirmationBody, {
            headers: {
                ...baseHeaders,
            },
        });
        return DOCUMENT_UPLOAD_STATE.SUCCEEDED;
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export const uploadDocumentToS3 = async ({
    setDocuments,
    uploadSession,
    document,
}: UploadDocumentsToS3Args) => {
    const documentMetadata: S3Upload = uploadSession[document.file.name];
    const formData = new FormData();
    const docFields: S3UploadFields = documentMetadata.fields;
    Object.entries(docFields).forEach(([key, value]) => {
        formData.append(key, value);
    });
    formData.append('file', document.file);
    const s3url = documentMetadata.url;
    try {
        return await axios.post(s3url, formData, {
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
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

const uploadDocuments = async ({
    nhsNumber,
    documents,
    baseUrl,
    baseHeaders,
}: UploadDocumentsArgs) => {
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
                attachment: documents.map((doc) => ({
                    fileName: doc.file.name,
                    contentType: doc.file.type,
                    docType: doc.docType,
                })),
            },
        ],
        created: new Date(Date.now()).toISOString(),
    };

    const gatewayUrl = baseUrl + endpoints.DOCUMENT_UPLOAD;

    try {
        const { data }: DocRefResponse = await axios.post(gatewayUrl, JSON.stringify(requestBody), {
            headers: {
                ...baseHeaders,
            },
        });
        return data;
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export const updateUploadDocumentState = async ({
    uploading,
    documents,
    uploadSession,
    baseUrl,
    baseHeaders,
}: UpdateUploadDocumentStateArgs) => {
    const virusScanGatewayUrl = baseUrl + endpoints.UPLOAD_DOCUMENT_STATE;

    try {
        const files = documents.map((doc) => {
            const documentMetadata = uploadSession[doc.file.name];
            const documentReference = documentMetadata.fields.key.split('/')[3];
            return {
                reference: documentReference,
                type: doc.docType,
                fields: [{ Uploading: `${uploading}` }],
            };
        });
        const body = {
            files,
        };
        const res = await axios.post(virusScanGatewayUrl, body, {
            headers: {
                ...baseHeaders,
            },
        });
        console.log(res);
        return res;
    } catch (e) {
        return DOCUMENT_UPLOAD_STATE.INFECTED;
    }
};

export default uploadDocuments;
