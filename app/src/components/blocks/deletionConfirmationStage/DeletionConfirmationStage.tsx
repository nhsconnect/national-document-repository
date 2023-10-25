import React, { Dispatch, SetStateAction } from 'react';
import { ButtonLink, Card } from 'nhsuk-react-components';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';

export type Props = {
    numberOfFiles: number;
    patientDetails: PatientDetails;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function DeletionConfirmationStage({ numberOfFiles, patientDetails, setStage }: Props) {
    const nhsNumber: String =
        patientDetails?.nhsNumber.slice(0, 3) +
        ' ' +
        patientDetails?.nhsNumber.slice(3, 6) +
        ' ' +
        patientDetails?.nhsNumber.slice(6, 10);

    return (
        <div className="deletion-complete">
            <Card style={{ maxWidth: '620px' }} className="deletion-complete-card">
                <Card.Content>
                    <Card.Heading style={{ margin: 'auto' }}>Deletion complete</Card.Heading>
                    <Card.Description style={{ fontSize: '16px' }}>
                        {numberOfFiles} files from the Lloyd George record of:{' '}
                    </Card.Description>
                    <Card.Description style={{ fontWeight: '700', fontSize: '24px' }}>
                        {patientDetails?.givenName?.map((name) => `${name} `)}
                        {patientDetails?.familyName}
                    </Card.Description>
                    <Card.Description style={{ fontSize: '16px' }}>
                        (NHS number: {nhsNumber})
                    </Card.Description>
                </Card.Content>
            </Card>
            <p style={{ marginTop: 40 }}>
                <ButtonLink onClick={() => setStage(LG_RECORD_STAGE.RECORD)}>
                    Return to patient's Lloyd George record page
                </ButtonLink>
            </p>
        </div>
    );
}

export default DeletionConfirmationStage;
