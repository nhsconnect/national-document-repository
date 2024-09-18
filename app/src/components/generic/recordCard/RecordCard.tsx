import { Card } from 'nhsuk-react-components';
import React, { ReactNode, useEffect, useRef, useState } from 'react';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import getLloydGeorgeRecord from '../../../helpers/requests/getLloydGeorgeRecord';
import PdfViewer from '../pdfViewer/PdfViewer';
import { AxiosError } from 'axios';
import { isMock } from '../../../helpers/utils/isLocal';
import useConfig from '../../../helpers/hooks/useConfig';
import { useNavigate } from 'react-router';
import usePatient from '../../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import ProgressBar from '../progressBar/ProgressBar';
import { routes } from '../../../types/generic/routes';
import { errorToParams } from '../../../helpers/utils/errorToParams';

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

    const isLoading = [
        DOWNLOAD_STAGE.INITIAL,
        DOWNLOAD_STAGE.PENDING,
        DOWNLOAD_STAGE.REFRESH,
    ].includes(downloadStage);

    useEffect(() => {
        const onSuccess = (presign_url: string) => {
            setDownloadStage(DOWNLOAD_STAGE.SUCCEEDED);
            setRecordUrl(presign_url);
        };

        const onError = (e: AxiosError) => {
            const error = e as AxiosError;

            if (isMock(error) && !!config.mockLocal.recordUploaded) {
                onSuccess('/dev/testFile.pdf');
            } else if (error.response?.status === 403) {
                navigate(routes.SESSION_EXPIRED);
            } else if (error.response?.status && error.response?.status >= 500) {
                navigate(routes.SERVER_ERROR + errorToParams(error));
            } else {
                setDownloadStage(DOWNLOAD_STAGE.FAILED);
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

    const Record = () => {
        if (isLoading) {
            return <ProgressBar status="Loading..." />;
        } else if (downloadStage === DOWNLOAD_STAGE.FAILED) {
            return null;
        }
        return <PdfViewer fileUrl={recordUrl} />;
    };

    const RecordLayout = ({ children }: { children: ReactNode }) => {
        if (isFullScreen) {
            return <div>{children}</div>;
        } else {
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
                    <div>{children}</div>
                </Card>
            );
        }
    };
    return (
        <RecordLayout>
            <Record />
        </RecordLayout>
    );
}

export default RecordCard;
