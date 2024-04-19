import { Card, Details } from 'nhsuk-react-components';
import React, { ReactNode } from 'react';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../pdfViewer/PdfViewer';

type Props = {
    downloadStage: DOWNLOAD_STAGE;
    recordUrl: string;
    heading: string;
    fullScreenHandler: (clicked: true) => void;
    children: ReactNode;
};

function RecordCard({ downloadStage, recordUrl, heading, fullScreenHandler, children }: Props) {
    return (
        <Card className="lloydgeorge_record-stage_pdf">
            <Card.Content data-testid="pdf-card" className="lloydgeorge_record-stage_pdf-content">
                <Card.Heading
                    className="lloydgeorge_record-stage_pdf-content-label"
                    headingLevel="h1"
                >
                    {/* Lloyd George record */}
                    {heading}
                </Card.Heading>
                {children}
            </Card.Content>
            {downloadStage === DOWNLOAD_STAGE.SUCCEEDED && (
                <Details expander open className="lloydgeorge_record-stage_pdf-expander">
                    <Details.Summary
                        style={{ display: 'inline-block' }}
                        data-testid="view-record-bin"
                    >
                        View record
                    </Details.Summary>
                    <button
                        className="lloydgeorge_record-stage_pdf-expander-button link-button clickable"
                        data-testid="full-screen-btn"
                        onClick={() => {
                            fullScreenHandler(true);
                        }}
                    >
                        View in full screen
                    </button>
                    <PdfViewer fileUrl={recordUrl} />
                </Details>
            )}
        </Card>
    );
}

export default RecordCard;
