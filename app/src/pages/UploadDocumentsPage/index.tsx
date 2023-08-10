import React, { useState } from 'react';
import SelectStage from '../../components/pages/UploadDocumentsPage/SelectStage';
import CompleteStage from '../../components/pages/UploadDocumentsPage/CompleteStage';
import UploadingStage from '../../components/pages/UploadDocumentsPage/UploadingStage';
import {
  StageProps,
  UPLOAD_STAGE,
  UploadDocument
} from '../../types/pages/UploadDocumentsPage/types';
import uploadDocument from '../../request/uploadDocument';

type Props = {};
function UploadDocumentsPage(props: Props) {
  const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
  const [documents, setDocuments] = useState<Array<UploadDocument>>([]);

  const mockPatient = {
    nhsNumber: '121212121'
  };

  const stageProps: StageProps = {
    stage,
    setStage
  };

  const uploadDocuments = async () => {
    await Promise.all(
      documents.map((document) =>
        uploadDocument({
          setStage,
          setDocuments,
          nhsNumber: mockPatient.nhsNumber,
          document
        })
      )
    );
  };

  if (stage === UPLOAD_STAGE.Selecting) {
    return <SelectStage {...stageProps} />;
  } else if (stage === UPLOAD_STAGE.Uploading) {
    return <UploadingStage {...stageProps} />;
  } else if (stage === UPLOAD_STAGE.Complete) {
    return <CompleteStage {...stageProps} />;
  }
  return null;
}

export default UploadDocumentsPage;
