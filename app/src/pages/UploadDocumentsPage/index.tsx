import React, { useState } from 'react';
import SelectStage from '../../components/pages/UploadDocumentsPage/SelectStage';
import CompleteStage from '../../components/pages/UploadDocumentsPage/CompleteStage';
import UploadingStage from '../../components/pages/UploadDocumentsPage/UploadingStage';
import {
  StageProps,
  UPLOAD_STAGE
} from '../../types/pages/UploadDocumentsPage/types';

type Props = {};
function UploadDocumentsPage(props: Props) {
  const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
  const stageProps: StageProps = {
    stage,
    setStage
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
