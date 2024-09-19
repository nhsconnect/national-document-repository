import { Card } from 'nhsuk-react-components';
import React, { ReactNode, useEffect, useRef, useState } from 'react';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../pdfViewer/PdfViewer';
import ProgressBar from '../progressBar/ProgressBar';

type Props = {
    heading: string;
    fullScreenHandler: (clicked: true) => void;
    detailsElement: ReactNode;
    downloadStage: DOWNLOAD_STAGE;
    isFullScreen: boolean;
    refreshRecord: () => void;
    cloudFrontUrl: string;
};

function RecordCard({
    heading,
    fullScreenHandler,
    detailsElement,
    isFullScreen,
    cloudFrontUrl,
    refreshRecord,
}: Props) {
    const [isLoading, setIsLoading] = useState(true);
    const mounted = useRef(false);
    useEffect(() => {
        const onPageLoad = async () => {
            await refreshRecord();
            setIsLoading(false);
        };
        if (!mounted.current) {
            mounted.current = true;
            void onPageLoad();
        }
    }, [refreshRecord]);
    // useEffect(() => {
    //     const onSuccess = (presign_url: string) => {
    //         setDownloadStage(DOWNLOAD_STAGE.SUCCEEDED);
    //         setRecordUrl(presign_url);
    //     };

    //     const onError = (e: AxiosError) => {
    //         const error = e as AxiosError;

    //         if (isMock(error) && !!config.mockLocal.recordUploaded) {
    //             onSuccess('/dev/testFile.pdf');
    //         } else if (error.response?.status === 403) {
    //             navigate(routes.SESSION_EXPIRED);
    //         } else if (error.response?.status && error.response?.status >= 500) {
    //             navigate(routes.SERVER_ERROR + errorToParams(error));
    //         } else {
    //             setDownloadStage(DOWNLOAD_STAGE.FAILED);
    //         }
    //     };

    //     const onPageLoad = async () => {
    //         const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    //         try {
    //             const { presign_url } = await getLloydGeorgeRecord({
    //                 nhsNumber,
    //                 baseUrl,
    //                 baseHeaders,
    //             });

    //             onSuccess(presign_url);
    //         } catch (e) {
    //             onError(e as AxiosError);
    //         }
    //     };
    //     if (!mounted.current) {
    //         mounted.current = true;
    //         void onPageLoad();
    //     }
    // }, [
    //     baseHeaders,
    //     baseUrl,
    //     config.mockLocal.recordUploaded,
    //     navigate,
    //     patientDetails?.nhsNumber,
    // ]);

    const Record = () => {
        if (isLoading) {
            return (
                <div className="pl-7">
                    <ProgressBar status="Loading..." />
                </div>
            );
        }
        return <PdfViewer fileUrl={cloudFrontUrl} />;
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

                        {cloudFrontUrl && (
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
