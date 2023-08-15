import React, { useState } from "react";
import SelectStage from "../../components/pages/UploadDocumentsPage/SelectStage";
import CompleteStage from "../../components/pages/UploadDocumentsPage/CompleteStage";
import UploadingStage from "../../components/pages/UploadDocumentsPage/UploadingStage";
import {
  DOCUMENT_UPLOAD_STATE,
  StageProps,
  UPLOAD_STAGE,
  UploadDocument,
} from "../../types/pages/UploadDocumentsPage/types";
import uploadDocument from "../../helpers/requests/uploadDocument";
import { useBaseAPIUrl } from "../../providers/configProvider/ConfigProvider";

type Props = {};
function UploadDocumentsPage(props: Props) {
  const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
  const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
  const baseUrl = useBaseAPIUrl("doc-store-api");

  const setDocumentState = (
    id: string,
    state: DOCUMENT_UPLOAD_STATE,
    progress?: number
  ) => {
    let shallowDocumentsCopy = documents;
    const hasDocument = documents.some((doc) => doc.id === id);
    if (hasDocument) {
      const idx = documents.findIndex((doc) => doc.id === id);
      if (progress) {
        shallowDocumentsCopy[idx].progress = progress;
      }
      if (state) {
        shallowDocumentsCopy[idx].state = state;
      }
    }
    setDocuments(shallowDocumentsCopy);
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

  const defaultStageProps: StageProps = {
    stage,
    setStage,
    documents,
  };

  if (stage === UPLOAD_STAGE.Selecting) {
    return (
      <SelectStage
        {...defaultStageProps}
        uploadDocuments={uploadDocuments}
        setDocuments={setDocuments}
      />
    );
  } else if (stage === UPLOAD_STAGE.Uploading) {
    return <UploadingStage {...defaultStageProps} />;
  } else if (stage === UPLOAD_STAGE.Complete) {
    return <CompleteStage {...defaultStageProps} />;
  }
  return null;
}

export default UploadDocumentsPage;
