import React from 'react';
import usePatient from '../../../helpers/hooks/usePatient';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
type Props = {
    separator?: boolean;
};
const PatientSummary = ({ separator = false }: Props) => {
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const dob: string = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';
    return (
        <div
            id="patient-info"
            className={`lloydgeorge_record-stage_patient-info ${separator ? 'separator' : ''}`}
        >
            <p data-testid="patient-name">
                {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
            </p>
            <p data-testid="patient-nhs-number">NHS number: {formattedNhsNumber}</p>
            <p data-testid="patient-dob">Date of birth: {dob}</p>
        </div>
    );
};

export default PatientSummary;
