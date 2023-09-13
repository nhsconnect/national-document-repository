import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../types/pages/UploadDocumentsPage/types';
import axios, { AxiosError } from 'axios';

type Args = {
    setDocumentState: (id: string, state: DOCUMENT_UPLOAD_STATE, progress?: number) => void;
    document: UploadDocument;
    nhsNumber: string;
    baseUrl: string;
    docType: DOCUMENT_TYPE;
};

const uploadDocument = async ({ nhsNumber, setDocumentState, document, baseUrl }: Args) => {
    const rawDoc = document.file;
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
                attachment: {
                    contentType: rawDoc.type,
                },
            },
        ],
        description: rawDoc.name,
        created: new Date(Date.now()).toISOString(),
    };

    setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.UPLOADING);
    const gatewayUrl = baseUrl + '/DocumentReference';

    try {
        const { data: gatewayResponse } = await axios.post(
            gatewayUrl,
            JSON.stringify(requestBody),
            {
                headers: {
                    'Content-Type': 'application/json',
                },
                params: {
                    documentType: document.docType.toString(),
                },
            },
        );
        const formData = new FormData();
        Object.keys(gatewayResponse.fields).forEach((key) => {
            formData.append(key, gatewayResponse.fields[key]);
        });
        formData.append('file', document.file);
        const s3url = gatewayResponse.url;

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
};

export default uploadDocument;
