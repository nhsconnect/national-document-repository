import { ReactNode, createContext, useContext } from 'react';
import usePatient from '../../../helpers/hooks/usePatient';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { SummaryList, Tag } from 'nhsuk-react-components';
import type { PatientDetails } from '../../../types/generic/patientDetails';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';

// Context for sharing patient data and configuration
type PatientSummaryContextType = {
    patientDetails: PatientDetails | null;
    joinNames?: boolean;
};

const PatientSummaryContext = createContext<PatientSummaryContextType | null>(null);

const usePatientSummaryContext = () => {
    const context = useContext(PatientSummaryContext);
    if (!context) {
        throw new Error('PatientSummary subcomponents must be used within PatientSummary');
    }
    return context;
};

// Main PatientSummary component
type PatientSummaryProps = {
    showDeceasedTag?: boolean;
    joinNames?: boolean;
    children?: ReactNode;
    // Legacy props for backward compatibility
    detailsToDisplay?: Array<
        keyof Pick<
            PatientDetails,
            'nhsNumber' | 'familyName' | 'givenName' | 'birthDate' | 'postalCode'
        >
    >;
};

const PatientSummary = ({ showDeceasedTag = false, children }: PatientSummaryProps) => {
    const patientDetails = usePatient();

    // If children are provided, use compound component pattern
    if (children) {
        return (
            <PatientSummaryContext.Provider value={{ patientDetails }}>
                <>
                    {showDeceasedTag && patientDetails?.deceased && (
                        <Tag color="blue" className="mb-6" data-testid="deceased-patient-tag">
                            Deceased patient
                        </Tag>
                    )}
                    <SummaryList id="patient-summary" data-testid="patient-summary">
                        {children}
                    </SummaryList>
                </>
            </PatientSummaryContext.Provider>
        );
    }

    return (
        <>
            {showDeceasedTag && patientDetails?.deceased && (
                <Tag color="blue" className="mb-6" data-testid="deceased-patient-tag">
                    Deceased patient
                </Tag>
            )}
            <PatientSummaryContext.Provider value={{ patientDetails }}>
                <SummaryList id="patient-summary" data-testid="patient-summary">
                    <PatientNhsNumber />
                    <PatientFamilyName />
                    <PatientGivenName />
                    <PatientDob />
                    <PatientPostcode />
                </SummaryList>
            </PatientSummaryContext.Provider>
        </>
    );
};

// Subcomponents
const PatientNhsNumber = () => {
    const { patientDetails } = usePatientSummaryContext();
    return (
        <SummaryList.Row>
            <SummaryList.Key>NHS number</SummaryList.Key>
            <SummaryList.Value
                data-testid="patient-summary-nhs-number"
                id="patient-summary-nhs-number"
            >
                {formatNhsNumber(patientDetails?.nhsNumber ?? '')}
            </SummaryList.Value>
        </SummaryList.Row>
    );
};

const PatientFullName = () => {
    const { patientDetails } = usePatientSummaryContext();

    return (
        <SummaryList.Row>
            <SummaryList.Key>Patient name</SummaryList.Key>
            <SummaryList.Value
                data-testid="patient-summary-full-name"
                id="patient-summary-full-name"
            >
                {`${patientDetails?.familyName}, ${patientDetails?.givenName?.join(' ')}`}
            </SummaryList.Value>
        </SummaryList.Row>
    );
};

const PatientGivenName = () => {
    const { patientDetails } = usePatientSummaryContext();
    return (
        <SummaryList.Row>
            <SummaryList.Key>First name</SummaryList.Key>
            <SummaryList.Value
                data-testid="patient-summary-given-name"
                id="patient-summary-given-name"
            >
                {patientDetails?.givenName?.join(' ')}
            </SummaryList.Value>
        </SummaryList.Row>
    );
};

const PatientFamilyName = () => {
    const { patientDetails } = usePatientSummaryContext();
    return (
        <SummaryList.Row>
            <SummaryList.Key>Surname</SummaryList.Key>
            <SummaryList.Value
                data-testid="patient-summary-family-name"
                id="patient-summary-family-name"
            >
                {patientDetails?.familyName}
            </SummaryList.Value>
        </SummaryList.Row>
    );
};

const PatientDob = () => {
    const { patientDetails } = usePatientSummaryContext();
    return (
        <SummaryList.Row>
            <SummaryList.Key>Date of birth</SummaryList.Key>
            <SummaryList.Value
                data-testid="patient-summary-date-of-birth"
                id="patient-summary-date-of-birth"
            >
                {patientDetails?.birthDate
                    ? getFormattedDate(new Date(patientDetails.birthDate))
                    : ''}
            </SummaryList.Value>
        </SummaryList.Row>
    );
};

const PatientPostcode = () => {
    const { patientDetails } = usePatientSummaryContext();
    return (
        <SummaryList.Row>
            <SummaryList.Key>Postcode</SummaryList.Key>
            <SummaryList.Value data-testid="patient-summary-postcode" id="patient-summary-postcode">
                {patientDetails?.postalCode}
            </SummaryList.Value>
        </SummaryList.Row>
    );
};

// Attach subcomponents to PatientSummary
PatientSummary.PatientNhsNumber = PatientNhsNumber;
PatientSummary.PatientFullName = PatientFullName;
PatientSummary.PatientGivenName = PatientGivenName;
PatientSummary.PatientFamilyName = PatientFamilyName;
PatientSummary.PatientDob = PatientDob;
PatientSummary.PatientPostcode = PatientPostcode;

export default PatientSummary;
