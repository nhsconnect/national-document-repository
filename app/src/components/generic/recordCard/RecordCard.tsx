import { Card } from 'nhsuk-react-components';
import React, { ReactNode, useEffect, useRef } from 'react';
import PdfViewer from '../pdfViewer/PdfViewer';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';

export type Props = {
    heading: string;
    fullScreenHandler: (clicked: true) => void;
    detailsElement: ReactNode;
    isFullScreen: boolean;
    refreshRecord: () => void;
    cloudFrontUrl: string;
    resetDocStage: () => void;
};

function RecordCard({
    heading,
    fullScreenHandler,
    detailsElement,
    isFullScreen,
    cloudFrontUrl,
    refreshRecord,
    resetDocStage,
}: Props) {
    const role = useRole();
    const userIsGpClinical = role === REPOSITORY_ROLE.GP_CLINICAL;
    const mounted = useRef(false);

    useEffect(() => {
        const onPageLoad = async () => {
            resetDocStage();
            await refreshRecord();
        };
        if (!mounted.current) {
            onPageLoad();
            mounted.current = true;
        }
    }, [refreshRecord, resetDocStage]);

    const Record = () => {
        return cloudFrontUrl ? <PdfViewer fileUrl={cloudFrontUrl} /> : null;
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

                        {cloudFrontUrl && !userIsGpClinical && (
                            <button
                                className="lloydgeorge_record-stage_pdf-content-button link-button clickable"
                                data-testid="full-screen-btn"
                                onClick={() => {
                                    fullScreenHandler(true);
                                    resetDocStage();
                                }}
                            >
                                View in full screen
                            </button>
                        )}
                        <p>
                            To search within this record use <strong>Control</strong> and{' '}
                            <strong>F</strong>
                        </p>
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
