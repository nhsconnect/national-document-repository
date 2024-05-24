import React, { useEffect, useRef, useState } from 'react';
import { UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import SelectStage from '../../components/blocks/_arf/selectStage/SelectStage';
import UploadingStage from '../../components/blocks/_arf/uploadingStage/UploadingStage';
import CompleteStage from '../../components/blocks/_arf/completeStage/CompleteStage';
import { routeChildren, routes } from '../../types/generic/routes';
import { Outlet, Route, Routes, useNavigate } from 'react-router';
import useConfig from '../../helpers/hooks/useConfig';
import { getLastURLPath } from '../../helpers/utils/urlManipulations';

function UploadDocumentsPage() {
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

    return (
        <>
            <Routes>
                <Route
                    index
                    element={<SelectStage setDocuments={setDocuments} documents={documents} />}
                ></Route>
                <Route
                    path={getLastURLPath(routeChildren.ARF_UPLOAD_UPLOADING)}
                    element={<UploadingStage documents={documents} />}
                ></Route>
                <Route
                    path={getLastURLPath(routeChildren.ARF_UPLOAD_COMPLETED)}
                    element={<CompleteStage documents={documents} />}
                ></Route>
            </Routes>
            <Outlet></Outlet>
        </>
    );
}

export default UploadDocumentsPage;
