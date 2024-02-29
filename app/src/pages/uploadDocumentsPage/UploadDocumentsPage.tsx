import React, { useEffect, useRef, useState } from 'react';
import { UPLOAD_STAGE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import SelectStage from '../../components/blocks/_arf/selectStage/SelectStage';
import UploadingStage from '../../components/blocks/_arf/uploadingStage/UploadingStage';
import CompleteStage from '../../components/blocks/_arf/completeStage/CompleteStage';
import { routes } from '../../types/generic/routes';
import { useNavigate } from 'react-router';
import useConfig from '../../helpers/hooks/useConfig';

function UploadDocumentsPage() {
    const [stage, setStage] = useState<UPLOAD_STAGE>(UPLOAD_STAGE.Selecting);
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const config = useConfig();
    const navigate = useNavigate();

    const mounted = useRef(false);
    useEffect(() => {
        const onPageLoad = () => {
            if (
                !config.featureFlags.uploadArfWorkflowEnabled ||
                !config.featureFlags.uploadLambdaEnabled
            ) {
                navigate(routes.UNAUTHORISED);
            }
        };

        if (!mounted.current) {
            mounted.current = true;
            onPageLoad();
        }
    }, [navigate, config]);

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
