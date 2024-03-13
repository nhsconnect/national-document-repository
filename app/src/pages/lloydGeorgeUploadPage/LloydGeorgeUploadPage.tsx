import React, { useState } from 'react';
import LloydGeorgeUploadingStage from '../../components/blocks/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage';
import { UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import LloydGeorgeFileInputStage from '../../components/blocks/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage';
import LloydGeorgeUploadComplete from '../../components/blocks/lloydGeorgeUploadComplete/LloydGeorgeUploadComplete';
import LloydGeorgeUploadFailure from '../../components/blocks/lloydGeorgeUploadFailure/LloydGeorgeUploadFailure';

export enum LG_UPLOAD_STAGE {
    SELECT = 0,
    UPLOAD = 1,
    COMPLETE = 2,
    INFECTED = 3,
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
            return <LloydGeorgeUploadingStage documents={documents} setStage={setStage} />;
        case LG_UPLOAD_STAGE.COMPLETE:
            return <LloydGeorgeUploadComplete documents={documents} />;
        case LG_UPLOAD_STAGE.INFECTED:
            return <LloydGeorgeUploadFailure documents={documents} setStage={setStage} />;
        default:
            return <div />;
    }
}

export default LloydGeorgeUploadPage;
