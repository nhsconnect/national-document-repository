import React, { useEffect, useRef, useState } from 'react';
import { DOCUMENT_UPLOAD_STATE, UploadDocument } from '../../types/pages/UploadDocumentsPage/types';
import SelectStage from '../../components/blocks/_arf/selectStage/SelectStage';
import UploadingStage from '../../components/blocks/_arf/uploadingStage/UploadingStage';
import CompleteStage from '../../components/blocks/_arf/completeStage/CompleteStage';
import { routeChildren, routes } from '../../types/generic/routes';
import { Outlet, Route, Routes, useNavigate } from 'react-router';
import useConfig from '../../helpers/hooks/useConfig';
import { getLastURLPath } from '../../helpers/utils/urlManipulations';
import { useLocation } from 'react-router-dom';

function UploadDocumentsPage() {
    const [documents, setDocuments] = useState<Array<UploadDocument>>([]);
    const config = useConfig();
    const navigate = useNavigate();
    const location = useLocation();

    const mounted = useRef(false);

    const allDocumentsSucceeded = documents.every(
        (document) => document.state === DOCUMENT_UPLOAD_STATE.SUCCEEDED,
    );
    const allDocumentsClean =
        documents.length > 0 &&
        documents.every((document) => document.state === DOCUMENT_UPLOAD_STATE.CLEAN);

    const allDocumentsFinishVirusScan =
        documents.length > 0 &&
        documents.every((document) =>
            [
                DOCUMENT_UPLOAD_STATE.CLEAN,
                DOCUMENT_UPLOAD_STATE.INFECTED,
                DOCUMENT_UPLOAD_STATE.SUCCEEDED,
            ].includes(document.state),
        );

    const isUploading = location.pathname === routeChildren.ARF_UPLOAD_UPLOADING;

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

    useEffect(() => {
        if (!isUploading) {
            return;
        }
        if (allDocumentsSucceeded) {
            navigate(routeChildren.ARF_UPLOAD_COMPLETED);
        } else if (allDocumentsFinishVirusScan && allDocumentsClean) {
            // eslint-disable-next-line no-console
            console.log('All documents are clean, run confirm lambda');
        } else if (allDocumentsFinishVirusScan) {
            // eslint-disable-next-line no-console
            console.log('some document are not clean');
        }
    }, [
        isUploading,
        allDocumentsClean,
        allDocumentsFinishVirusScan,
        allDocumentsSucceeded,
        navigate,
    ]);

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
