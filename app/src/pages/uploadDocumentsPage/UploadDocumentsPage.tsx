import React, { useState } from 'react';
import { UPLOAD_STAGE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import SelectStage from '../../components/blocks/_arf/selectStage/SelectStage';
import UploadingStage from '../../components/blocks/_arf/uploadingStage/UploadingStage';
import CompleteStage from '../../components/blocks/_arf/completeStage/CompleteStage';

function UploadDocumentsPage() {
    const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);

    if (stage === UPLOAD_STAGE.Selecting) {
        return (
            <SelectStage setDocuments={setDocuments} setStage={setStage} documents={documents} />
        );
    } else if (stage === UPLOAD_STAGE.Uploading) {
        return <UploadingStage documents={documents} />;
    } else if (stage === UPLOAD_STAGE.Complete) {
        return <CompleteStage documents={documents} />;
    }
    return null;
}

export default UploadDocumentsPage;
