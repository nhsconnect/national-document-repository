import React, {
    Dispatch,
    SetStateAction,
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';
import { Card } from 'nhsuk-react-components';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import getPresignedUrlForZip from '../../../../helpers/requests/getPresignedUrlForZip';
import { DOCUMENT_TYPE } from '../../../../types/pages/UploadDocumentsPage/types';
import LgDownloadComplete from '../lloydGeorgeDownloadComplete/LloydGeorgeDownloadComplete';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import usePatient from '../../../../helpers/hooks/usePatient';
import deleteAllDocuments from '../../../../helpers/requests/deleteAllDocuments';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { useNavigate, Link, Routes, Route, Outlet } from 'react-router-dom';
import { errorToParams } from '../../../../helpers/utils/errorToParams';
import { AxiosError } from 'axios/index';
import { isMock } from '../../../../helpers/utils/isLocal';
import useConfig from '../../../../helpers/hooks/useConfig';
import useTitle from '../../../../helpers/hooks/useTitle';
import { getLastURLPath } from '../../../../helpers/utils/urlManipulations';

const FakeProgress = require('fake-progress');

export type Props = {
    numberOfFiles: number;
    // setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    deleteAfterDownload: boolean;
    // setDownloadStage: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
};

type DownloadLinkAttributes = {
    url: string;
    filename: string;
};

function LloydGeorgeDownloadAllStage({ numberOfFiles, deleteAfterDownload = false }: Props) {
    const timeToComplete = 600;
    const [progress, setProgress] = useState(0);
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const [linkAttributes, setLinkAttributes] = useState<DownloadLinkAttributes>({
        url: '',
        filename: '',
    });
    const linkRef = useRef<HTMLAnchorElement | null>(null);
    const mounted = useRef(false);
    const navigate = useNavigate();
    const { mockLocal } = useConfig();
    const patientDetails = usePatient();
    const nhsNumber = patientDetails?.nhsNumber ?? '';
    const [delayTimer, setDelayTimer] = useState<NodeJS.Timeout>();

    const progressTimer = useMemo(() => {
        return new FakeProgress({
            timeConstant: timeToComplete,
            autoStart: true,
        });
    }, []);
    const intervalTimer = window.setInterval(() => {
        setProgress(parseInt((progressTimer.progress * 100).toFixed(1)));
    }, 100);

    const handlePageExit = useCallback(() => {
        window.clearInterval(intervalTimer);
        if (delayTimer) {
            window.clearTimeout(delayTimer);
        }
    }, [delayTimer, intervalTimer]);

    useEffect(() => {
        if (linkRef.current && linkAttributes.url) {
            linkRef?.current?.click();
            setTimeout(() => {
                navigate(routeChildren.LLOYD_GEORGE_DOWNLOAD_COMPLETE);
            }, 600);
        }
    }, [linkAttributes, navigate]);

    useEffect(() => {
        const onFail = (error: AxiosError) => {
            if (isMock(error) && !!mockLocal.recordUploaded) {
                if (typeof window !== 'undefined') {
                    const { protocol, host } = window.location;
                    setLinkAttributes({
                        url: protocol + '//' + host + '/dev/testFile.pdf',
                        filename: 'testFile.pdf',
                    });
                }
            } else if (error.response?.status === 403) {
                navigate(routes.SESSION_EXPIRED);
            } else {
                navigate(routes.SERVER_ERROR + errorToParams(error));
            }
        };
        const onPageLoad = async () => {
            progressTimer.stop();
            window.clearInterval(intervalTimer);
            try {
                const preSignedUrl = await getPresignedUrlForZip({
                    baseUrl,
                    baseHeaders,
                    nhsNumber,
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                });

                const filename = `patient-record-${nhsNumber}`;
                if (deleteAfterDownload) {
                    try {
                        await deleteAllDocuments({
                            docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                            nhsNumber: nhsNumber,
                            baseUrl,
                            baseHeaders,
                        });
                    } catch (e) {
                        const error = e as AxiosError;
                        onFail(error);
                    } // This is fail and forget at this point in time.
                }
                setLinkAttributes({ url: preSignedUrl, filename: filename });
            } catch (e) {
                const error = e as AxiosError;
                onFail(error);
            }
        };

        if (!mounted.current) {
            mounted.current = true;
            const min = timeToComplete - 100;
            const max = timeToComplete + 200;
            const delay = Math.floor(Math.random() * (max - min + 1) + min);
            const delayTimer = setTimeout(onPageLoad, timeToComplete + delay);
            setDelayTimer(delayTimer);
        }
    }, [
        baseHeaders,
        baseUrl,
        intervalTimer,
        nhsNumber,
        progressTimer,
        deleteAfterDownload,
        navigate,
        mockLocal,
    ]);
    const pageHeader = 'Downloading documents';
    useTitle({ pageTitle: pageHeader });
    return (
        <>
            <Routes>
                <Route
                    index
                    element={
                        <div
                            className="lloydgeorge_downloadall-stage"
                            data-testid="lloydgeorge_downloadall-stage"
                        >
                            <div className="lloydgeorge_downloadall-stage_header">
                                <h1>{pageHeader}</h1>
                                <h2>
                                    {patientDetails?.givenName + ' ' + patientDetails?.familyName}
                                </h2>
                                <h4>NHS number: {patientDetails?.nhsNumber}</h4>
                                <div className="nhsuk-heading-xl" />
                                <h4>Preparing download for {numberOfFiles} files</h4>
                            </div>

                            <Card className="lloydgeorge_downloadall-stage_details">
                                <Card.Content>
                                    <strong>
                                        <p>Compressing record into a zip file</p>
                                    </strong>

                                    <div className="lloydgeorge_downloadall-stage_details-content">
                                        <div>
                                            <span>
                                                {`${linkAttributes.url ? 100 : progress}%`}{' '}
                                                downloaded...
                                            </span>
                                            <a
                                                hidden
                                                id="download-link"
                                                data-testid={linkAttributes.url}
                                                ref={linkRef}
                                                href={linkAttributes.url}
                                                download
                                            >
                                                Download Lloyd George Documents URL
                                            </a>
                                        </div>
                                        <div>
                                            <Link
                                                to="#"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    handlePageExit();
                                                    navigate(routes.LLOYD_GEORGE);
                                                }}
                                            >
                                                Cancel
                                            </Link>
                                        </div>
                                    </div>
                                </Card.Content>
                            </Card>
                        </div>
                    }
                />
                <Route
                    path={getLastURLPath(routeChildren.LLOYD_GEORGE_DOWNLOAD_COMPLETE)}
                    element={<LgDownloadComplete deleteAfterDownload={deleteAfterDownload} />}
                />
            </Routes>

            <Outlet />
        </>
    );
}

export default LloydGeorgeDownloadAllStage;
