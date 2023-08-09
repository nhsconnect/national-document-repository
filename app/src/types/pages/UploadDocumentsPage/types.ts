import type { Dispatch, SetStateAction } from 'react';

export enum UPLOAD_STAGE {
  Selecting = 0,
  Uploading = 1,
  Complete = 2
}

export type StageProps = {
  stage: UPLOAD_STAGE;
  setStage: Dispatch<SetStateAction<UPLOAD_STAGE>>;
};
