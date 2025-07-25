import { ReactNode, createContext, useContext } from 'react';
import usePatient from '../../../helpers/hooks/usePatient';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { SummaryList, Tag } from 'nhsuk-react-components';
import type { PatientDetails } from '../../../types/generic/patientDetails';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';

/**
 * Props for the PatientSummary component.
 *
 * @property {boolean} [showDeceasedTag] - Optional flag to display a deceased tag for the patient.
 * @property {ReactNode} [children] - Optional React children to be rendered within the component.
 */
type PatientSummaryProps = {
    showDeceasedTag?: boolean;
    children?: ReactNode;
};

// Context for sharing patient data and configuration
type PatientSummaryContextType = {
    patientDetails: PatientDetails | null;
};

const PatientSummaryContext = createContext<PatientSummaryContextType | null>(null);

const usePatientSummaryContext = () => {
    const context = useContext(PatientSummaryContext);
    if (!context) {
        throw new Error('PatientSummary subcomponents must be used within PatientSummary');
    }
    return context;
};

/**
 * Enum representing the keys for patient summary items.
 *
 * @remarks
 * Used to identify and access specific patient information fields.
 *
 * @enum {string}
 * @property {string} NHS_NUMBER - Patient's NHS number.
 * @property {string} FAMILY_NAME - Patient's family name.
 * @property {string} GIVEN_NAME - Patient's given name.
 * @property {string} BIRTH_DATE - Patient's date of birth.
 * @property {string} POSTAL_CODE - Patient's postal code.
 * @property {string} FULL_NAME - Patient's full name, combining family and given names.
 */
export enum PatientInfo {
    NHS_NUMBER,
    FAMILY_NAME,
    GIVEN_NAME,
    BIRTH_DATE,
    POSTAL_CODE,
    FULL_NAME,
}

const summaryRow = (key: string, elementId: string, value: ReactNode) => {
    return (
        <SummaryList.Row>
            <SummaryList.Key>{key}</SummaryList.Key>
            <SummaryList.Value data-testid={elementId} id={elementId}>
                {value}
            </SummaryList.Value>
        </SummaryList.Row>
    );
};

/**
 * Sub-component of PatientSummary that renders a summary row for a specific patient detail.
 *
 * @param item - The type of patient information to display, as defined by the PatientInfo enum.
 * @returns A React element representing a summary row for the specified patient detail.
 */
const Details: React.FC<{ item: PatientInfo }> = ({ item }) => {
    const { patientDetails } = usePatientSummaryContext();
    let key, elementId, value;

    switch (item) {
        case PatientInfo.FULL_NAME:
            key = 'Patient name';
            elementId = 'patient-summary-full-name';
            value = `${patientDetails?.familyName}, ${patientDetails?.givenName?.join(' ')}`;
            break;
        case PatientInfo.NHS_NUMBER:
            key = 'NHS number';
            elementId = 'patient-summary-nhs-number';
            value = formatNhsNumber(patientDetails?.nhsNumber ?? '');
            break;
        case PatientInfo.FAMILY_NAME:
            key = 'Surname';
            elementId = 'patient-summary-family-name';
            value = patientDetails?.familyName ?? '';
            break;
        case PatientInfo.GIVEN_NAME:
            key = 'First name';
            elementId = 'patient-summary-given-name';
            value = patientDetails?.givenName?.join(' ') ?? '';
            break;
        case PatientInfo.BIRTH_DATE:
            key = 'Date of birth';
            elementId = 'patient-summary-date-of-birth';
            value = patientDetails?.birthDate
                ? getFormattedDate(new Date(patientDetails.birthDate))
                : '';
            break;
        case PatientInfo.POSTAL_CODE:
            key = 'Postcode';
            elementId = 'patient-summary-postal-code';
            value = patientDetails?.postalCode ?? '';
            break;
        default:
            return <></>;
    }

    return summaryRow(key, elementId, value);
};

/**
 * Patient summary component that displays key information about a patient.
 *
 * @param showDeceasedTag - Optional flag to display a tag for deceased patients.
 * @param children - Optional child components to be rendered inside the summary.
 * @returns A React element representing the patient summary.
 */
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
                    <Details item={PatientInfo.NHS_NUMBER} />
                    <Details item={PatientInfo.FAMILY_NAME} />
                    <Details item={PatientInfo.GIVEN_NAME} />
                    <Details item={PatientInfo.BIRTH_DATE} />
                    <Details item={PatientInfo.POSTAL_CODE} />
                </SummaryList>
            </PatientSummaryContext.Provider>
        </>
    );
};

/**
 * Sub-component of PatientSummary that renders a summary row for a specific patient detail.
 *
 * @param item - The type of patient information to display, as defined by the PatientInfo enum.
 * @returns A React element representing a summary row for the specified patient detail.
 */
PatientSummary.Child = Details;

export default PatientSummary;
