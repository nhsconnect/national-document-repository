import { Card } from 'nhsuk-react-components';
import React, { ReactNode } from 'react';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import PdfViewer from '../pdfViewer/PdfViewer';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';

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
    const role = useRole();
    const userIsGpAdmin = role === REPOSITORY_ROLE.GP_ADMIN;

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
                {downloadStage === DOWNLOAD_STAGE.SUCCEEDED && userIsGpAdmin && (
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
            {downloadStage === DOWNLOAD_STAGE.SUCCEEDED && (
                <div className="lloydgeorge_record-stage_pdf-expander">
                    <PdfViewer fileUrl={recordUrl} />
                </div>
            )}
        </Card>
    );
}

export default RecordCard;
