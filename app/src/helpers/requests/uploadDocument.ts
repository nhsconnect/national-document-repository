import { AuthHeaders } from '../../types/blocks/authHeaders';
import { endpoints } from '../../types/generic/endpoints';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../types/pages/UploadDocumentsPage/types';
import axios, { AxiosError } from 'axios';
import { S3Upload, S3UploadFields, UploadResult } from '../../types/generic/uploadResult';

type UploadDocumentsArgs = {
    setDocumentState: (id: string, state: DOCUMENT_UPLOAD_STATE, progress?: number) => void;
    documents: UploadDocument[];
    nhsNumber: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
    docType: DOCUMENT_TYPE;
};

type UploadDocumentsToS3Args = {
    setDocumentState: (id: string, state: DOCUMENT_UPLOAD_STATE, progress?: number) => void;
    documents: UploadDocument[];
    data: UploadResult;
};

type gatewayResponse = {
    data: UploadResult;
};

const uploadDocument = async ({
    nhsNumber,
    setDocumentState,
    documents,
    baseUrl,
    baseHeaders,
}: UploadDocumentsArgs) => {
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
        await uploadDocumentsToS3({ setDocumentState, documents, data });
    } catch (e) {
        const error = e as AxiosError;
        if (error.response?.status === 403) {
            documents.forEach((document) => {
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.UNAUTHORISED);
            });
            return;
        } else {
            documents.forEach((document) => {
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.FAILED);
            });
            return;
        }
    }
};

const uploadDocumentsToS3 = async ({
    setDocumentState,
    documents,
    data,
}: UploadDocumentsToS3Args) => {
    for (const document of documents) {
        try {
            const docGatewayResponse: S3Upload = data[document.file.name];
            const formData = new FormData();
            const docFields: S3UploadFields = docGatewayResponse.fields;
            Object.keys(docFields).forEach((key) => {
                formData.append(key, docFields.key);
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

            if (s3Response.status === 204)
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.SUCCEEDED);
        } catch (e) {
            const error = e as AxiosError;
            if (error.response?.status === 403) {
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.UNAUTHORISED);
            } else {
                setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.FAILED);
            }
        }
    }
};

export default uploadDocument;
