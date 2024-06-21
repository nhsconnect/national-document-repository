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
import waitForSeconds from '../utils/waitForSeconds';
import {
    DELAY_BETWEEN_VIRUS_SCAN_RETRY_IN_SECONDS,
    setSingleDocument,
} from '../utils/uploadAndScanDocumentHelpers';

const VIRUS_SCAN_RETRY_LIMIT = 3;
const TIMEOUT_ERROR_STATUS_CODE = 504;
const TIMEOUT_ERROR = 'TIMEOUT_ERROR';

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

export type UpdateStateArgs = {
    documents: UploadDocument[];
    uploadingState: boolean;
    baseUrl: string;
    baseHeaders: AuthHeaders;
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

export const virusScanResult = async (virusScanArgs: VirusScanArgs) => {
    for (let i = 0; i < VIRUS_SCAN_RETRY_LIMIT; i++) {
        const scanResult = await requestVirusScan(virusScanArgs);
        if (scanResult === TIMEOUT_ERROR) {
            await waitForSeconds(DELAY_BETWEEN_VIRUS_SCAN_RETRY_IN_SECONDS);
            continue;
        }
        return scanResult;
    }

    throw new Error(`Virus scan api calls timed-out for ${VIRUS_SCAN_RETRY_LIMIT} attempts.`);
};

const requestVirusScan = async ({ documentReference, baseUrl, baseHeaders }: VirusScanArgs) => {
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
        const error = e as AxiosError;
        if (error.response?.status === TIMEOUT_ERROR_STATUS_CODE) {
            return TIMEOUT_ERROR;
        }
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
        const fileUUID = documentMetadata.fields.key.split('/').at(-1);
        const previousKeys = acc[doc.docType] ?? [];

        return {
            ...acc,
            [doc.docType]: [...previousKeys, fileUUID],
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
                    setSingleDocument(setDocuments, {
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

export const updateDocumentState = async ({
    documents,
    uploadingState,
    baseUrl,
    baseHeaders,
}: UpdateStateArgs) => {
    const updateUploadStateUrl = baseUrl + endpoints.UPLOAD_DOCUMENT_STATE;
    const body = {
        files: documents.map((document) => ({
            reference: document.ref,
            type: document.docType,
            fields: { Uploading: uploadingState },
        })),
    };
    try {
        return await axios.post(updateUploadStateUrl, body, {
            headers: {
                ...baseHeaders,
            },
        });
    } catch (e) {}
};

export default uploadDocuments;
