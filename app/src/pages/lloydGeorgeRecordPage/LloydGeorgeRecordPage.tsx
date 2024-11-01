import React, { useState } from 'react';
import { DOWNLOAD_STAGE } from '../../types/generic/downloadStage';

import LloydGeorgeViewRecordStage from '../../components/blocks/_lloydGeorge/lloydGeorgeViewRecordStage/LloydGeorgeViewRecordStage';
import { LG_RECORD_STAGE } from '../../types/blocks/lloydGeorgeStages';
import useRole from '../../helpers/hooks/useRole';
import useIsBSOL from '../../helpers/hooks/useIsBSOL';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import { routeChildren, routes } from '../../types/generic/routes';
import { Outlet, Route, Routes, useNavigate } from 'react-router-dom';
import { getLastURLPath } from '../../helpers/utils/urlManipulations';
import RemoveRecordStage from '../../components/blocks/_delete/removeRecordStage/RemoveRecordStage';
import LloydGeorgeSelectDownloadStage from '../../components/blocks/_lloydGeorge/lloydGeorgeSelectDownloadStage/LloydGeorgeSelectDownloadStage';
import { AxiosError } from 'axios';
import { ErrorResponse } from '../../types/generic/errorResponse';
import { isMock } from '../../helpers/utils/isLocal';
import useConfig from '../../helpers/hooks/useConfig';
import moment from 'moment';
import { errorToParams } from '../../helpers/utils/errorToParams';
import usePatient from '../../helpers/hooks/usePatient';
import getLloydGeorgeRecord from '../../helpers/requests/getLloydGeorgeRecord';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import { getFormattedDatetime } from '../../helpers/utils/formatDatetime';

function LloydGeorgeRecordPage() {
    const [downloadStage, setDownloadStage] = useState(DOWNLOAD_STAGE.INITIAL);
    const [stage, setStage] = useState(LG_RECORD_STAGE.RECORD);
    const role = useRole();
    const isBSOL = useIsBSOL();
    const deleteAfterDownload = role === REPOSITORY_ROLE.GP_ADMIN && !isBSOL;
    const config = useConfig();
    const navigate = useNavigate();
    const patientDetails = usePatient();
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();

    const [numberOfFiles, setNumberOfFiles] = useState(0);
    const [totalFileSizeInBytes, settotalFileSizeInBytes] = useState(0);
    const [lastUpdated, setLastUpdated] = useState('');
    const [cloudFrontUrl, setCloudFrontUrl] = useState('');

    const resetDocState = () => {
        setNumberOfFiles(0);
        setLastUpdated('');
        settotalFileSizeInBytes(0);
        setCloudFrontUrl('');
        setDownloadStage(DOWNLOAD_STAGE.INITIAL);
    };

    const refreshRecord = async () => {
        const onSuccess = (
            filesCount: number,
            updatedDate: string,
            fileSize: number,
            presignedUrl: string,
        ) => {
            setNumberOfFiles(filesCount);
            setLastUpdated(getFormattedDatetime(new Date(updatedDate)));
            setDownloadStage(DOWNLOAD_STAGE.SUCCEEDED);
            settotalFileSizeInBytes(fileSize);
            setCloudFrontUrl(presignedUrl);
        };

        const onError = (e: AxiosError) => {
            const error = e as AxiosError;
            const errorResponse = (error.response?.data as ErrorResponse) ?? {};

            if (isMock(error)) {
                if (!!config.mockLocal.recordUploaded) {
                    onSuccess(1, moment().format(), 59000, '/dev/testFile.pdf');
                } else {
                    setDownloadStage(DOWNLOAD_STAGE.NO_RECORDS);
                }
            } else {
                if (error.response?.status === 504) {
                    setDownloadStage(DOWNLOAD_STAGE.TIMEOUT);
                } else if (
                    error.response?.status === 404 ||
                    (error.response?.status === 400 && errorResponse?.err_code === 'LGL_400')
                ) {
                    setDownloadStage(DOWNLOAD_STAGE.NO_RECORDS);
                } else if (error.response?.status === 403) {
                    navigate(routes.SESSION_EXPIRED);
                } else if (error.response?.status && error.response?.status >= 500) {
                    navigate(routes.SERVER_ERROR + errorToParams(error));
                } else if (error.response?.status === 423) {
                    setDownloadStage(DOWNLOAD_STAGE.UPLOADING);
                } else {
                    setDownloadStage(DOWNLOAD_STAGE.FAILED);
                }
            }
        };

        const nhsNumber: string = patientDetails?.nhsNumber ?? '';
        try {
            const { numberOfFiles, totalFileSizeInBytes, lastUpdated, presignedUrl } =
                await getLloydGeorgeRecord({
                    nhsNumber,
                    baseUrl,
                    baseHeaders,
                });

            onSuccess(numberOfFiles, lastUpdated, totalFileSizeInBytes, presignedUrl);
        } catch (e) {
            onError(e as AxiosError);
        }
    };

    return (
        <>
            <Routes>
                <Route
                    index
                    element={
                        <LloydGeorgeViewRecordStage
                            downloadStage={downloadStage}
                            setStage={setStage}
                            stage={stage}
                            lastUpdated={lastUpdated}
                            totalFileSizeInBytes={totalFileSizeInBytes}
                            numberOfFiles={numberOfFiles}
                            refreshRecord={refreshRecord}
                            cloudFrontUrl={cloudFrontUrl}
                        />
                    }
                />
                <Route
                    path={getLastURLPath(routeChildren.LLOYD_GEORGE_DOWNLOAD) + '/*'}
                    element={
                        <LloydGeorgeSelectDownloadStage
                            setDownloadStage={setDownloadStage}
                            deleteAfterDownload={deleteAfterDownload}
                            numberOfFiles={numberOfFiles}
                        />
                    }
                />
                <Route
                    path={getLastURLPath(routeChildren.LLOYD_GEORGE_DELETE) + '/*'}
                    element={
                        <RemoveRecordStage
                            setDownloadStage={setDownloadStage}
                            numberOfFiles={numberOfFiles}
                            recordType="Lloyd George"
                            resetDocState={resetDocState}
                        />
                    }
                />
            </Routes>

            <Outlet />
        </>
    );
}

export default LloydGeorgeRecordPage;
