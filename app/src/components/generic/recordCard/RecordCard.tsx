import { Card } from 'nhsuk-react-components';
import React, { ReactNode, useEffect, useRef, useState } from 'react';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../pdfViewer/PdfViewer';
import ProgressBar from '../progressBar/ProgressBar';

export type Props = {
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
