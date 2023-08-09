import React, { useState } from 'react';
import SelectStage from '../../components/pages/UploadDocumentsPage/SelectStage';
import UploadStage from '../../components/pages/UploadDocumentsPage/UploadStage';
import CompleteStage from '../../components/pages/UploadDocumentsPage/CompleteStage';
import {
  StageProps,
  UPLOAD_STAGE
} from '../../types/pages/UploadDocumentsPage/types';

type Props = {};
const UploadDocumentsPage = (props: Props) => {
  const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
  const stageProps: StageProps = {
    stage,
    setStage
  };

  if (stage === UPLOAD_STAGE.Selecting) {
    return <SelectStage {...stageProps} />;
  } else if (stage === UPLOAD_STAGE.Uploading) {
    return <UploadStage {...stageProps} />;
  } else if (stage === UPLOAD_STAGE.Complete) {
    return <CompleteStage {...stageProps} />;
  }
};

export default UploadDocumentsPage;
