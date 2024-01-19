import React, { Dispatch, SetStateAction } from 'react';
import { Button, Card } from 'nhsuk-react-components';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../helpers/hooks/usePatient';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';

export type Props = {
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    setDownloadStage: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
    deleteAfterDownload: boolean;
};

function LloydGeorgeDownloadComplete({ setStage, setDownloadStage, deleteAfterDownload }: Props) {
    const patientDetails = usePatient();

    const handleReturnButtonClick = () => {
        setStage(LG_RECORD_STAGE.RECORD);
        if (deleteAfterDownload) {
            setDownloadStage(DOWNLOAD_STAGE.REFRESH);
        }
    };

    return (
        <div className="lloydgeorge_download-complete">
            <Card className="lloydgeorge_download-complete_details">
                <Card.Content className="lloydgeorge_download-complete_details-content">
                    <Card.Heading className="lloydgeorge_download-complete_details-content_header">
                        Download complete
                    </Card.Heading>
                    Documents from the Lloyd George record of:
                    <div className="lloydgeorge_download-complete_details-content_subheader">
                        <strong>
                            {patientDetails?.givenName + ' ' + patientDetails?.familyName}
                        </strong>
                    </div>
                    <div>{`(NHS number: ${patientDetails?.nhsNumber})`}</div>
                </Card.Content>
            </Card>
            <Button onClick={handleReturnButtonClick} data-testid="return-btn">
                Return to patient's available medical records
            </Button>
        </div>
    );
}

export default LloydGeorgeDownloadComplete;
