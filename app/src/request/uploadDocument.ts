import {
  DOCUMENT_UPLOAD_STATE,
  UploadDocument
} from '../types/pages/UploadDocumentsPage/types';

type Args = {
  setDocumentState: (
    id: string,
    state?: DOCUMENT_UPLOAD_STATE,
    progress?: number
  ) => void;
  document: UploadDocument;
  nhsNumber: string;
};

const uploadDocument = async ({
  setDocumentState,
  nhsNumber,
  document
}: Args) => {
  const rawDoc = document.file;
  const requestBody = {
    resourceType: 'DocumentReference',
    subject: {
      identifier: {
        system: 'https://fhir.nhs.uk/Id/nhs-number',
        value: nhsNumber
      }
    },
    type: {
      coding: [
        {
          system: 'http://snomed.info/sct',
          code: '22151000087106'
        }
      ]
    },
    content: [
      {
        attachment: {
          contentType: rawDoc.type
        }
      }
    ],
    description: rawDoc.name,
    created: new Date(Date.now()).toISOString()
  };

  setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.UPLOADING);
  const gatewayUrl = '/DocumentReference';

  try {
    const gatewayResponse = await fetch(gatewayUrl, {
      body: JSON.stringify(requestBody)
    }).then((res) => res.json());
    const s3url = gatewayResponse.data.content[0].attachment.url;
    console.log('GATEWAY RESPONSE: ', gatewayResponse);
    const s3Response = await fetch(s3url, {
      method: 'PUT',
      headers: {
        'Content-Type': rawDoc.type
      },
      body: rawDoc
    });
    setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.SUCCEEDED);
    console.log('S3 RESPONSE: ', s3Response);
  } catch (e: any) {
    console.error(e);
    if (e.response?.status === 403) {
      setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.UNAUTHORISED);
    } else {
      setDocumentState(document.id, DOCUMENT_UPLOAD_STATE.FAILED);
    }
  }
};

export default uploadDocument;
