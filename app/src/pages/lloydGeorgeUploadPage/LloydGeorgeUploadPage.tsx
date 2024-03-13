import React, { useState } from 'react';
import LloydGeorgeUploadingStage from '../../components/blocks/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage';
import { UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import LloydGeorgeFileInputStage from '../../components/blocks/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage';
import LloydGeorgeUploadFailure from '../../components/blocks/lloydGeorgeUploadFailure/LloydGeorgeUploadFailure';
import LloydGeorgeUploadCompleteStage from '../../components/blocks/lloydGeorgeUploadCompleteStage/LloydGeorgeUploadCompleteStage';
import LloydGeorgeRetryUploadStage from '../../components/blocks/lloydGeorgeRetryUploadStage/LloydGeorgeRetryUploadStage';
import { UploadSession } from '../../types/generic/uploadResult';

export enum LG_UPLOAD_STAGE {
    SELECT = 0,
    UPLOAD = 1,
    COMPLETE = 2,
    INFECTED = 3,
    RETRY = 4,
}

function LloydGeorgeUploadPage() {
    const [stage, setStage] = useState<LG_UPLOAD_STAGE>(LG_UPLOAD_STAGE.SELECT);
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const [uploadSession, setUploadSession] = useState<UploadSession | null>(null);
    switch (stage) {
        case LG_UPLOAD_STAGE.SELECT:
            return (
                <LloydGeorgeFileInputStage
                    setStage={setStage}
                    documents={documents}
                    setDocuments={setDocuments}
                    setUploadSession={setUploadSession}
                />
            );
        case LG_UPLOAD_STAGE.UPLOAD:
            return (
                <LloydGeorgeUploadingStage
                    documents={documents}
                    setStage={setStage}
                    setDocuments={setDocuments}
                    uploadSession={uploadSession}
                />
            );
        case LG_UPLOAD_STAGE.COMPLETE:
            return <LloydGeorgeUploadCompleteStage documents={documents} />;
        case LG_UPLOAD_STAGE.INFECTED:
            return <LloydGeorgeUploadFailure documents={documents} setStage={setStage} />;
        case LG_UPLOAD_STAGE.RETRY:
            return <LloydGeorgeRetryUploadStage setStage={setStage} />;
        default:
            return <div />;
    }
}

export default LloydGeorgeUploadPage;
