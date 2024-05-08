import React, { Dispatch, SetStateAction } from 'react';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import useTitle from '../../../../helpers/hooks/useTitle';
import { BackLink, WarningCallout } from 'nhsuk-react-components';
import PatientSummary from '../../../generic/patientSummary/PatientSummary';

export type Props = {
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function LloydGeorgeRemoveRecordStage({ setStage }: Props) {
    useTitle({ pageTitle: 'Remove record' });

    return (
        <>
            <BackLink
                data-testid="back-link"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    setStage(LG_RECORD_STAGE.RECORD);
                }}
            >
                Go back
            </BackLink>
            <h1>Remove this Lloyd George record</h1>
            <WarningCallout>
                <WarningCallout.Label>Before removing</WarningCallout.Label>
                <p>
                    Only permanently remove this patient record if you have a valid reason to. For
                    example, you confirmed these files have reached the end of their retention
                    period.
                </p>
            </WarningCallout>
            <PatientSummary />
        </>
    );
}
export default LloydGeorgeRemoveRecordStage;
