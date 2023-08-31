import React from "react";
import UploadSummary from "./UploadSummary";
import { Button } from "nhsuk-react-components";
import { useNavigate } from "react-router";
import { UploadDocument } from "../../../types/pages/UploadDocumentsPage/types";
interface Props {
  documents: Array<UploadDocument>;
}

function CompleteStage({ documents }: Props) {
  const navigate = useNavigate();

  return (
    <>
      <UploadSummary documents={documents}></UploadSummary>
      <p style={{ fontWeight: "600" }}>
        If you want to upload another patient&apos;s health record
      </p>
      <Button
        onClick={() => {
          navigate("/");
        }}
      >
        Start Again
      </Button>
    </>
  );
}

export default CompleteStage;
