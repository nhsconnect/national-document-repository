import type { Dispatch, SetStateAction } from 'react';

export type SetUploadStage = Dispatch<SetStateAction<UPLOAD_STAGE>>;
export type SetUploadDocuments = Dispatch<
  SetStateAction<Array<UploadDocument>>
>;

export enum UPLOAD_STAGE {
  Selecting = 0,
  Uploading = 1,
  Complete = 2
}

export enum DOCUMENT_UPLOAD_STATE {
  SELECTED = 0,
  UPLOADING = 1,
  SUCCEEDED = 2,
  FAILED = 3,
  UNAUTHORISED = 4
}

export type StageProps = {
  stage: UPLOAD_STAGE;
  setStage: SetUploadStage;
  documents: Array<UploadDocument>;
};

export type UploadDocument = {
  state: DOCUMENT_UPLOAD_STATE;
  file: File;
  progress: number;
  id: string;
};
