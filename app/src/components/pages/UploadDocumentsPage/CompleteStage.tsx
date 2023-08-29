import React from 'react';
import { StageProps } from '../../../types/pages/UploadDocumentsPage/types';
import UploadSummary from "./UploadSummary";
import {Button} from "nhsuk-react-components";
import {useNavigate} from "react-router";

function CompleteStage({ stage, setStage, documents }: StageProps) {
  const navigate = useNavigate();

  return <>
    <UploadSummary documents={documents} setStage={setStage} stage={stage}></UploadSummary>
    <p style={{fontWeight: "600"}}>If you want to upload another patient&apos;s health record</p>
    <Button
        onClick={() => {
          navigate('/');
        }}
    >
      Start Again
    </Button>
  </>;
}

export default CompleteStage;

