import usePatient from '../../../helpers/hooks/usePatient';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { getFormattedDate } from '../../../helpers/utils/formatDate';

type Props = {
    separator?: boolean;
};

const PatientSimpleSummary = ({ separator = false }: Props) => {
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const dob: string = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    const nameLengthLimit = 30;
    const givenName = patientDetails?.givenName.join(' ') || '';
    const familyName = patientDetails?.familyName || '';
    const longname = givenName.length + familyName.length > nameLengthLimit;

    return (
        <div
            id="patient-info"
            data-testid="patient-info"
            className={`lloydgeorge_record-stage_patient-info ${separator ? 'separator' : ''}`}
        >
            <p>
                <span
                    data-testid="patient-name"
                    className="nhsuk-u-padding-right-9 nhsuk-u-font-weight-bold"
                >
                    {`${patientDetails?.givenName}, ${patientDetails?.familyName}`}
                </span>

                {longname && <br />}

                <span data-testid="patient-nhs-number" className="nhsuk-u-padding-right-9">
                    NHS number: {formattedNhsNumber}
                </span>
                <span data-testid="patient-dob">Date of birth: {dob}</span>
            </p>
        </div>
    );
};

export default PatientSimpleSummary;
