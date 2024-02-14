import React, { useState } from 'react';
import LloydGeorgeUploadingStage from '../../components/blocks/lloydGeorgeUploadingStage/LloydGeorgeUploadingStage';
import { UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import LloydGeorgeFileInputStage from '../../components/blocks/lloydGeorgeFileInputStage/LloydGeorgeFileInputStage';

type Props = {};

export enum LG_UPLOAD_STAGE {
    SELECT = 0,
    UPLOAD = 1,
    COMPLETE = 2,
}

function LloydGeorgeUploadPage({}: Props) {
    const [stage, setStage] = useState<LG_UPLOAD_STAGE>(LG_UPLOAD_STAGE.SELECT);
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    // const files = [
    //     buildTextFile('1of3_Lloyd_George_Record_[Barry ONEIL]_[9730182000]_[23-10-2018]', 100),
    //     buildTextFile('2of3_Lloyd_George_Record_[Barry ONEIL]_[9730182000]_[23-10-2018]', 101),
    // ];
    // const documents = files.map((file) => {
    //     return {
    //         ...buildDocument(file, DOCUMENT_UPLOAD_STATE.SUCCEEDED),
    //         progress: 100,
    //     };
    // });
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
            return (
                // TODO, ADD UPLOAD COMPLETE STAGE
                <div>
                    <button
                        onClick={() => {
                            setStage(LG_UPLOAD_STAGE.SELECT);
                        }}
                    >
                        back to upload
                    </button>
                    <div>upload complete</div>
                </div>
            );
        default:
            return null;
    }
}

export default LloydGeorgeUploadPage;
