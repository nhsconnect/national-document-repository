import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../types/pages/UploadDocumentsPage/types';
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
    setDocumentState: (
        id: string,
        state: DOCUMENT_UPLOAD_STATE,
        progress?: number | undefined,
    ) => void;
    documents: UploadDocument[];
    data: UploadResult;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type gatewayResponse = {
    data: UploadResult;
};

type KeyByType = {
    [propName in DOCUMENT_TYPE]: string[];
};

const uploadDocument = async ({
    nhsNumber,
    setDocuments,
    documents,
    baseUrl,
    baseHeaders,
}: UploadDocumentsArgs) => {
    const setDocumentState = (
        id: string,
        state: DOCUMENT_UPLOAD_STATE,
        progress?: number | undefined,
    ) => {
        setDocuments((prevDocuments: UploadDocument[]) => {
            return prevDocuments.map((document) => {
                if (document.id === id) {
                    progress =
                        state === DOCUMENT_UPLOAD_STATE.SCANNING
                            ? progress
                            : progress ?? document.progress;

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
    const uploadConfirmationGatewayUrl = baseUrl + endpoints.UPLOAD_CONFIRMATION;

    const confirmationBody = {
        patientId: nhsNumber,
        documents: {},
    };
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
        confirmationBody.documents = await uploadDocumentsToS3({
            setDocumentState,
            documents,
            data,
            baseUrl,
            baseHeaders,
        });
        console.log('confirmation body:' + confirmationBody);
        await axios.post(uploadConfirmationGatewayUrl, confirmationBody, {
            headers: {
                ...baseHeaders,
            },
        });
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
    baseHeaders,
}: UploadDocumentsToS3Args) => {
    const virusScanGatewayUrl = baseUrl + endpoints.VIRUS_SCAN;
    const filesKeyByType = {} as KeyByType;
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
            console.log('S3 RESPONSE' + s3Response);
            const requestBody = {
                documentReference: docGatewayResponse.fields.key,
            };
            console.log('REQUEST BODY' + requestBody);
            if (s3Response.status === 204) {
                try {
                    console.log('IN S3 TRY');
                    setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.SCANNING, undefined);
                    await axios.post(virusScanGatewayUrl, requestBody, {
                        headers: {
                            ...baseHeaders,
                        },
                    });
                } catch (e) {
                    console.log('IN S3 catch');

                    const error = e as AxiosError;
                    if (error.response?.status === 400) {
                        setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.INFECTED);
                    }
                    throw e;
                }
            }
            const fileKey = docGatewayResponse.fields.key.split('/');
            console.log('file key' + fileKey);
            setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.SUCCEEDED, 100);
            const array = filesKeyByType[document.docType] ?? [];
            console.log('array ' + array);
            filesKeyByType[document.docType] = [...array, fileKey[2]];
            console.log('object files key' + filesKeyByType);
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
    return filesKeyByType;
};

export default uploadDocument;
