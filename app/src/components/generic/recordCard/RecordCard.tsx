import { Card } from 'nhsuk-react-components';
import React, { ReactNode } from 'react';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../pdfViewer/PdfViewer';

type Props = {
    recordUrl: string;
    heading: string;
    fullScreenHandler: (clicked: true) => void;
    detailsElement: ReactNode;
    downloadStage: DOWNLOAD_STAGE;
};

function RecordCard({
    downloadStage,
    recordUrl,
    heading,
    fullScreenHandler,
    detailsElement,
}: Props) {
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

                {/* TODO: MOVE BUTTON HERE AND UPDATE CLASSNAME  */}
                {/* {/* <button
                        className="lloydgeorge_record-stage_pdf-expander-button link-button clickable full-screen-btn"
                        data-testid="full-screen-btn"
                        onClick={() => {
                            fullScreenHandler(true);
                        }}
                    >
                        View in full screen
                    </button> */}
            </Card.Content>
            {downloadStage === DOWNLOAD_STAGE.SUCCEEDED && (
                <div className="lloydgeorge_record-stage_pdf-expander">
                    {/* <button
                        className="lloydgeorge_record-stage_pdf-expander-button link-button clickable full-screen-btn"
                        data-testid="full-screen-btn"
                        onClick={() => {
                            fullScreenHandler(true);
                        }}
                    >
                        View in full screen
                    </button> */}
                    <PdfViewer fileUrl={recordUrl} />
                </div>
            )}
        </Card>
    );
}

export default RecordCard;
