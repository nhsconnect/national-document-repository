import usePatient from '../../../helpers/hooks/usePatient';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { SummaryList, Tag } from 'nhsuk-react-components';
type Props = {
    showDeceasedTag?: boolean;
};
const PatientSummary = ({ showDeceasedTag = false }: Props) => {
    const patientDetails = usePatient();
    return (
        <>
            {showDeceasedTag && patientDetails?.deceased && (
                <Tag color="blue" className="mb-6" data-testid="deceased-patient-tag">
                    Deceased patient
                </Tag>
            )}
            <SummaryList id="patient-summary" data-testid="patient-summary">
                <SummaryList.Row>
                    <SummaryList.Key>NHS number</SummaryList.Key>
                    <SummaryList.Value id="patient-summary-nhs-number">
                        {patientDetails?.nhsNumber}
                    </SummaryList.Value>
                </SummaryList.Row>
                <SummaryList.Row>
                    <SummaryList.Key>Surname</SummaryList.Key>
                    <SummaryList.Value id="patient-summary-family-name">
                        {patientDetails?.familyName}
                    </SummaryList.Value>
                </SummaryList.Row>
                <SummaryList.Row>
                    <SummaryList.Key>First name</SummaryList.Key>
                    <SummaryList.Value id="patient-summary-given-name">
                        {patientDetails?.givenName?.map((name) => `${name} `)}
                    </SummaryList.Value>
                </SummaryList.Row>
                <SummaryList.Row>
                    <SummaryList.Key>Date of birth</SummaryList.Key>
                    <SummaryList.Value id="patient-summary-date-of-birth">
                        {getFormattedDate(new Date(patientDetails?.birthDate ?? ''))}
                    </SummaryList.Value>
                </SummaryList.Row>
                <SummaryList.Row>
                    <SummaryList.Key>Postcode</SummaryList.Key>
                    <SummaryList.Value id="patient-summary-postcode">
                        {patientDetails?.postalCode}
                    </SummaryList.Value>
                </SummaryList.Row>
            </SummaryList>
        </>
    );
};

export default PatientSummary;
