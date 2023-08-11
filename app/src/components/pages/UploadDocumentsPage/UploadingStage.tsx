import React from 'react';
import {
  StageProps,
  UploadDocument
} from '../../../types/pages/UploadDocumentsPage/types';

function UploadingStage({ stage, setStage, documents }: StageProps) {
  const docs = documents.map((doc: UploadDocument) => ({
    ...doc,
    file: doc.file.name
  }));
  return <div>{JSON.stringify(docs)}</div>;
}

export default UploadingStage;
