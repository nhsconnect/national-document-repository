import React, { useState } from "react";
import SelectStage from "../../components/pages/UploadDocumentsPage/SelectStage";
import CompleteStage from "../../components/pages/UploadDocumentsPage/CompleteStage";
import UploadingStage from "../../components/pages/UploadDocumentsPage/UploadingStage";
import {
  DOCUMENT_UPLOAD_STATE,
  UPLOAD_STAGE,
  UploadDocument,
} from "../../types/pages/UploadDocumentsPage/types";
import uploadDocument from "../../helpers/requests/uploadDocument";
import { useBaseAPIUrl } from "../../providers/configProvider/ConfigProvider";

type Props = {};
function UploadDocumentsPage(props: Props) {
  const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
  const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
  const baseUrl = useBaseAPIUrl();

  console.log(baseUrl)
  const setDocumentState = (
    id: string,
    state: DOCUMENT_UPLOAD_STATE,
    progress?: number
  ) => {
    setDocuments((prevDocuments) => {
      const updatedDocuments = prevDocuments.map((document) => {
        if (document.id === id) {
          progress = progress ?? document.progress;
          return { ...document, state, progress };
        }
        return document;
      });
      return updatedDocuments;
    });
  };

  const mockPatient = {
    nhsNumber: "121212121",
  };

  const uploadDocuments = async () => {
    setStage(UPLOAD_STAGE.Uploading);
    await Promise.all(
      documents.map((document) =>
        uploadDocument({
          setDocumentState,
          nhsNumber: mockPatient.nhsNumber,
          document,
          baseUrl,
        })
      )
    );
    setStage(UPLOAD_STAGE.Complete);
  };

  if (stage === UPLOAD_STAGE.Selecting) {
    return (
      <SelectStage
        uploadDocuments={uploadDocuments}
        setDocuments={setDocuments}
      />
    );
  } else if (stage === UPLOAD_STAGE.Uploading) {
    return <UploadingStage documents={documents} />;
  } else if (stage === UPLOAD_STAGE.Complete) {
    return <CompleteStage documents={documents} />;
  }
  return null;
}

export default UploadDocumentsPage;
