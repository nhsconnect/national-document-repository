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
            <Card style={{ maxWidth: '620px' }}>
                <Card.Content
                    style={{
                        textAlign: 'center',
                        backgroundColor: '#555',
                        color: '#fff',
                        padding: '38px',
                        fontSize: '20px',
                    }}
                >
                    <Card.Heading style={{ fontSize: '48px' }}>Download complete</Card.Heading>
                    Documents from the Lloyd George record of:
                    <div style={{ fontSize: '34px' }}>
                        <strong>
                            {patientDetails.givenName + ' ' + patientDetails.familyName}
                        </strong>
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
