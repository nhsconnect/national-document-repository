import React from 'react';
import { Button } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import UploadSummary from '../uploadSummary/UploadSummary';
interface Props {
    documents: Array<UploadDocument>;
}

function CompleteStage({ documents }: Props) {
    const navigate = useNavigate();

    return (
        <>
            <UploadSummary documents={documents} />
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
