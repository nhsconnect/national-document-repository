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

type UploadDocumentsArgs = {
    setDocuments: Dispatch<SetStateAction<UploadDocument[]>>;
    setUploadSession: Dispatch<SetStateAction<UploadSession | null>>;
    documents: UploadDocument[];
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type UploadDocumentsToS3Args = {
    baseUrl: string;
    baseHeaders: AuthHeaders;
    setDocuments: Dispatch<SetStateAction<UploadDocument[]>>;
    documents: UploadDocument[];
    uploadSession: UploadSession;
};

type DocRefResponse = {
    data: UploadSession;
};

type DocumentStateProps = {
    id: string;
    state: DOCUMENT_UPLOAD_STATE;
    progress?: number | 'scan';
    attempts?: number;
};

type VirusScanArgs = {
    docRef: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};
type UploadConfirmationArgs = {
    baseUrl: string;
    baseHeaders: AuthHeaders;
    nhsNumber: string;
    documentKeysByType: FileKeyBuilder;
};
type FileKeyBuilder = {
    [key in DOCUMENT_TYPE]: string[];
};

export const setDocument = (
    setDocuments: Dispatch<SetStateAction<UploadDocument[]>>,
    { id, state, progress, attempts }: DocumentStateProps,
) => {
    setDocuments((prevState) =>
        prevState.map((document) => {
            if (document.id === id) {
                if (progress === 'scan') {
                    progress = undefined;
                } else {
                    progress = progress ?? document.progress;
                }
                attempts = attempts ?? document.attempts;
                state = state ?? document.state;
                return { ...document, state, progress, attempts };
            }
            return document;
        }),
    );
};

const virusScanResult = async ({ docRef, baseUrl, baseHeaders }: VirusScanArgs) => {
    const virusScanGatewayUrl = baseUrl + endpoints.VIRUS_SCAN;
    const body = { documentReference: docRef };
    await axios.post(virusScanGatewayUrl, body, {
        headers: {
            ...baseHeaders,
        },
    });
};

// const uploadConfirmation = async ({
//     baseUrl,
//     baseHeaders,
//     nhsNumber,
//     documentKeysByType,
// }: UploadConfirmationArgs) => {
//     const uploadConfirmationGatewayUrl = baseUrl + endpoints.UPLOAD_CONFIRMATION;
//     const confirmationBody = {
//         patientId: nhsNumber,
//         documents: { documentKeysByType },
//     };
//     await axios.post(uploadConfirmationGatewayUrl, confirmationBody, {
//         headers: {
//             ...baseHeaders,
//         },
//     });
// };

export const uploadDocumentsToS3 = async ({
    baseUrl,
    baseHeaders,
    setDocuments,
    uploadSession,
    documents,
}: UploadDocumentsToS3Args) => {
    // TODO: COPY FILEYKEYBUILDER LOGIC INTO UPLOAD CONFIRMATION

    // let fileKeyBuilder: FileKeyBuilder = {} as FileKeyBuilder;

    for (const document of documents) {
        const docGatewayResponse: S3Upload = uploadSession[document.file.name];
        const formData = new FormData();
        const docFields: S3UploadFields = docGatewayResponse.fields;
        Object.entries(docFields).forEach(([key, value]) => {
            formData.append(key, value);
        });
        formData.append('file', document.file);
        const s3url = docGatewayResponse.url;
        try {
            await axios.post(s3url, formData, {
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

            setDocument(setDocuments, {
                id: document.id,
                state: DOCUMENT_UPLOAD_STATE.SCANNING,
                progress: 'scan',
            });
            const docRef = docGatewayResponse.fields.key;
            try {
                await virusScanResult({ docRef, baseUrl, baseHeaders });
                setDocument(setDocuments, {
                    id: document.id,
                    state: DOCUMENT_UPLOAD_STATE.CLEAN,
                    progress: 100,
                });
            } catch {
                setDocument(setDocuments, {
                    id: document.id,
                    state: DOCUMENT_UPLOAD_STATE.INFECTED,
                    progress: 0,
                });
            }
            // const fileKey = docGatewayResponse.fields.key.split('/');
            // const currentFileKeys = fileKeyBuilder[document.docType] ?? [];
            // fileKeyBuilder[document.docType] = [...currentFileKeys, fileKey[3]];
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

const uploadDocuments = async ({
    nhsNumber,
    setDocuments,
    setUploadSession,
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
        setUploadSession(data);
        await uploadDocumentsToS3({
            setDocuments,
            documents,
            uploadSession: data,
            baseUrl,
            baseHeaders,
        });
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

export default uploadDocuments;
