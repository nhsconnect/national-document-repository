import {
  SetUploadDocuments,
  SetUploadStage,
  UPLOAD_STAGE,
  UploadDocument
} from '../types/pages/UploadDocumentsPage/types';

type Args = {
  setStage: SetUploadStage;
  setDocuments: SetUploadDocuments;
  document: UploadDocument;
  nhsNumber: string;
};

const uploadDocument = async ({
  setStage,
  setDocuments,
  nhsNumber,
  document
}: Args) => {
  const rawDoc = document.data;
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

  setStage(UPLOAD_STAGE.Uploading);
  console.log('UPLOAD STARTED');
  const gatewayUrl = '/DocumentReference';

  try {
    const gatewayResponse = await fetch(gatewayUrl, {
      body: JSON.stringify(requestBody)
    }).then((res) => res.json());
    const s3url = gatewayResponse.data.content[0].attachment.url;
    console.error('GATEWAY RESPONSE: ', gatewayResponse);

    const s3Response = await fetch(s3url, {
      method: 'PUT',
      headers: {
        'Content-Type': rawDoc.type
      },
      body: rawDoc
    });
    console.error('S3 RESPONSE: ', s3Response);
  } catch (e: any) {
    console.error('UPLOAD FAILED');
    if (e.response?.status === 403) {
      console.error('UPLOAD UNAUTHORISED');
    }
  }
};

export default uploadDocument;
