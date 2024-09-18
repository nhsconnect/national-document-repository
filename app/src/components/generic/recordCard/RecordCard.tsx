import { Card } from 'nhsuk-react-components';
import React, { ReactNode, useEffect, useRef, useState } from 'react';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import getLloydGeorgeRecord from '../../../helpers/requests/getLloydGeorgeRecord';
import PdfViewer from '../pdfViewer/PdfViewer';
import { AxiosError } from 'axios';
import { ErrorResponse } from '../../../types/generic/errorResponse';
import { isMock } from '../../../helpers/utils/isLocal';
import useConfig from '../../../helpers/hooks/useConfig';
import { errorToParams } from '../../../helpers/utils/errorToParams';
import { useNavigate } from 'react-router';
import { routes } from '../../../types/generic/routes';
import usePatient from '../../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';

type Props = {
    heading: string;
    fullScreenHandler: (clicked: true) => void;
    detailsElement: ReactNode;
    downloadStage: DOWNLOAD_STAGE;
    isFullScreen: boolean;
};

function RecordCard({ heading, fullScreenHandler, detailsElement, isFullScreen }: Props) {
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const config = useConfig();
    const [recordUrl, setRecordUrl] = useState('');
    const navigate = useNavigate();
    const patientDetails = usePatient();
    const mounted = useRef(false);
    const [downloadStage, setDownloadStage] = useState<DOWNLOAD_STAGE>(DOWNLOAD_STAGE.INITIAL);
    useEffect(() => {
        const onSuccess = (presign_url: string) => {
            setRecordUrl(presign_url);
        };

        const onError = (e: AxiosError) => {
            const error = e as AxiosError;
            const errorResponse = (error.response?.data as ErrorResponse) ?? {};

            if (isMock(error)) {
                if (!!config.mockLocal.recordUploaded) {
                    onSuccess('/dev/testFile.pdf');
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

        const onPageLoad = async () => {
            const nhsNumber: string = patientDetails?.nhsNumber ?? '';
            try {
                const { presign_url } = await getLloydGeorgeRecord({
                    nhsNumber,
                    baseUrl,
                    baseHeaders,
                });

                onSuccess(presign_url);
            } catch (e) {
                onError(e as AxiosError);
            }
        };
        if (!mounted.current) {
            mounted.current = true;
            void onPageLoad();
        }
    }, [
        baseHeaders,
        baseUrl,
        config.mockLocal.recordUploaded,
        navigate,
        patientDetails?.nhsNumber,
    ]);

    const Layout = ({ children }: { children: ReactNode }) => {
        if (isFullScreen) {
            return (
                <Card className="lloydgeorge_record-stage_pdf">
                    <Card.Content
                        data-testid="pdf-card"
                        className="lloydgeorge_record-stage_pdf-content"
                    >
                        <Card.Heading
                            className="lloydgeorge_record-stage_pdf-content-label"
                            headingLevel="h2"
                        >
                            {heading}
                        </Card.Heading>
                        {detailsElement}

                        {recordUrl && (
                            <button
                                className="lloydgeorge_record-stage_pdf-content-button link-button clickable"
                                data-testid="full-screen-btn"
                                onClick={() => {
                                    fullScreenHandler(true);
                                }}
                            >
                                View in full screen
                            </button>
                        )}
                    </Card.Content>
                    {recordUrl && (
                        <div className="lloydgeorge_record-stage_pdf-expander">{children}</div>
                    )}
                </Card>
            );
        } else {
            return children;
        }
    };
    return (
        <Card className="lloydgeorge_record-stage_pdf">
            <Card.Content data-testid="pdf-card" className="lloydgeorge_record-stage_pdf-content">
                <Card.Heading
                    className="lloydgeorge_record-stage_pdf-content-label"
                    headingLevel="h2"
                >
                    {heading}
                </Card.Heading>
                {detailsElement}

                {recordUrl && (
                    <button
                        className="lloydgeorge_record-stage_pdf-content-button link-button clickable"
                        data-testid="full-screen-btn"
                        onClick={() => {
                            fullScreenHandler(true);
                        }}
                    >
                        View in full screen
                    </button>
                )}
            </Card.Content>
            {recordUrl && (
                <div className="lloydgeorge_record-stage_pdf-expander">
                    <Layout>
                        <PdfViewer fileUrl={recordUrl} />;
                    </Layout>
                </div>
            )}
        </Card>
    );
}

export default RecordCard;
