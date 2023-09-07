import React from 'react';
import { Button } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { UploadDocument } from '../../../types/pages/UploadDocumentsPage/types';
import UploadSummary from '../uploadSummary/UploadSummary';
import { PatientDetails } from '../../../types/generic/patientDetails';
interface Props {
    documents: Array<UploadDocument>;
    patientDetails: PatientDetails;
}

function CompleteStage({ documents, patientDetails }: Props) {
    const navigate = useNavigate();

    return (
        <>
            <UploadSummary patientDetails={patientDetails} documents={documents} />
            <p style={{ fontWeight: '600' }}>
                If you want to upload another patient&apos;s health record
            </p>
            <Button
                id="start-again-button"
                onClick={() => {
                    navigate('/');
                }}
            >
                Start Again
            </Button>
        </>
    );
}

export default CompleteStage;
