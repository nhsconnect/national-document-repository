import React, { useState } from 'react';
import LloydGeorgeUploadingStage from '../../components/blocks/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage';
import { UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import LloydGeorgeFileInputStage from '../../components/blocks/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage';
import LloydGeorgeUploadCompleteStage from '../../components/blocks/lloydGeorgeUploadCompleteStage/LloydGeorgeUploadCompleteStage';
import LloydGeorgeRetryUploadStage from '../../components/blocks/lloydGeorgeRetryUploadStage/LloydGeorgeRetryUploadStage';

export enum LG_UPLOAD_STAGE {
    SELECT = 0,
    UPLOAD = 1,
    COMPLETE = 2,
    RETRY = 3,
}

function LloydGeorgeUploadPage() {
    const [stage, setStage] = useState<LG_UPLOAD_STAGE>(LG_UPLOAD_STAGE.SELECT);
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);

    switch (stage) {
        case LG_UPLOAD_STAGE.SELECT:
            return (
                <LloydGeorgeFileInputStage
                    setStage={setStage}
                    documents={documents}
                    setDocuments={setDocuments}
                />
            );
        case LG_UPLOAD_STAGE.UPLOAD:
            return (
                <LloydGeorgeUploadingStage
                    documents={documents}
                    setStage={setStage}
                    setDocuments={setDocuments}
                />
            );
        case LG_UPLOAD_STAGE.COMPLETE:
            return <LloydGeorgeUploadCompleteStage documents={documents} />;
        case LG_UPLOAD_STAGE.RETRY:
            return <LloydGeorgeRetryUploadStage />;
        default:
            return <div />;
    }
}

export default LloydGeorgeUploadPage;
