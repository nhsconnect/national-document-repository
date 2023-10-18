import React, { Dispatch, SetStateAction } from 'react';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { Button, Card } from 'nhsuk-react-components';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';

type Props = {
    patientDetails: PatientDetails;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function LgDownloadComplete({ patientDetails, setStage }: Props) {
    return (
        <>
            <Card>
                <Card.Heading>Download complete</Card.Heading>
                <Card.Content>
                    Documents from the Lloyd George record of:
                    <div style={{ fontSize: '18px' }}>
                        {patientDetails.givenName + ' ' + patientDetails.familyName}
                    </div>
                    <div>{`(NHS number: ${patientDetails.nhsNumber})`}</div>
                </Card.Content>
            </Card>
            <Button onClick={() => setStage(LG_RECORD_STAGE.RECORD)}>
                Return to patient's available medical records
            </Button>
        </>
    );
}

export default LgDownloadComplete;
