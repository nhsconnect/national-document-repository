import React, { Dispatch, SetStateAction } from 'react';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { Button, Card } from 'nhsuk-react-components';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';

export type Props = {
    patientDetails: PatientDetails;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function LloydGeorgeDownloadComplete({ patientDetails, setStage }: Props) {
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
                            {patientDetails.givenName + ' ' + patientDetails.familyName}
                        </strong>
                    </div>
                    <div>{`(NHS number: ${patientDetails.nhsNumber})`}</div>
                </Card.Content>
            </Card>
            <Button onClick={() => setStage(LG_RECORD_STAGE.RECORD)} data-testid="return-btn">
                Return to patient's available medical records
            </Button>
        </div>
    );
}

export default LloydGeorgeDownloadComplete;
