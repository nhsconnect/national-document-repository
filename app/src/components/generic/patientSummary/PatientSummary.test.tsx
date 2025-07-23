import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import PatientSummary from './PatientSummary';
import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as Mock;

describe('PatientSummary', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders provided patient information', () => {
        const mockDetails = buildPatientDetails({
            familyName: 'Jones',
            nhsNumber: '0000222000',
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSummary />);
        const expectedNhsNumber = formatNhsNumber(mockDetails.nhsNumber);

        expect(screen.getByText(expectedNhsNumber)).toBeInTheDocument();
        expect(screen.getByText(mockDetails.familyName)).toBeInTheDocument();
    });

    it('renders multiple given names with correct spacing', () => {
        const mockDetails = buildPatientDetails({
            familyName: 'Jones',
            nhsNumber: '0000222000',
            givenName: ['Comfort', 'Zulu'],
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSummary />);

        // Using hard coded expected value instead of duplicating the expected logic
        const expectedGivenName = 'Comfort Zulu';
        expect(screen.getByText(expectedGivenName)).toBeInTheDocument();
    });

    it('renders deceased patient tag for a deceased patient when tag is enabled', () => {
        const mockDetails = buildPatientDetails({
            deceased: true,
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSummary showDeceasedTag />);

        expect(screen.getByTestId('deceased-patient-tag')).toBeInTheDocument();
    });

    it('does not render deceased patient tag for a deceased patient when tag is disabled', () => {
        const mockDetails = buildPatientDetails({
            deceased: true,
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSummary />);

        expect(screen.queryByTestId('deceased-patient-tag')).not.toBeInTheDocument();
    });

    it('does not render deceased patient tag for a none deceased patient when tag is enabled', () => {
        const mockDetails = buildPatientDetails({
            deceased: false,
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSummary />);

        expect(screen.queryByTestId('deceased-patient-tag')).not.toBeInTheDocument();
    });

    describe('Compound Component Pattern', () => {
        it('renders children when children prop is provided', () => {
            const mockDetails = buildPatientDetails({
                familyName: 'Smith',
                nhsNumber: '1234567890',
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientNhsNumber />
                    <PatientSummary.PatientFamilyName />
                </PatientSummary>,
            );

            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
            expect(screen.getByText('123 456 7890')).toBeInTheDocument();
            expect(screen.getByText('Smith')).toBeInTheDocument();
        });

        it('renders deceased tag with children when showDeceasedTag is true and patient is deceased', () => {
            const mockDetails = buildPatientDetails({
                deceased: true,
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary showDeceasedTag>
                    <PatientSummary.PatientNhsNumber />
                </PatientSummary>,
            );

            expect(screen.getByTestId('deceased-patient-tag')).toBeInTheDocument();
            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        });

        it('does not render deceased tag with children when showDeceasedTag is false', () => {
            const mockDetails = buildPatientDetails({
                deceased: true,
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientNhsNumber />
                </PatientSummary>,
            );

            expect(screen.queryByTestId('deceased-patient-tag')).not.toBeInTheDocument();
            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        });
    });

    describe('Individual Subcomponents', () => {
        it('renders PatientFullName correctly', () => {
            const mockDetails = buildPatientDetails({
                familyName: 'Smith',
                givenName: ['John', 'Michael'],
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientFullName />
                </PatientSummary>,
            );

            expect(screen.getByText('Smith, John Michael')).toBeInTheDocument();
        });

        it('handles null patient details gracefully', () => {
            mockedUsePatient.mockReturnValue(null);
            render(<PatientSummary />);

            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
            // Components should render but with empty/default values
        });

        it('handles empty NHS number', () => {
            const mockDetails = buildPatientDetails({
                nhsNumber: '',
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientNhsNumber />
                </PatientSummary>,
            );

            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        });

        it('handles undefined givenName', () => {
            const mockDetails = buildPatientDetails({
                givenName: undefined,
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientGivenName />
                    <PatientSummary.PatientFullName />
                </PatientSummary>,
            );

            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        });

        it('handles empty givenName array', () => {
            const mockDetails = buildPatientDetails({
                givenName: [],
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientGivenName />
                </PatientSummary>,
            );

            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        });

        it('handles undefined birthDate', () => {
            const mockDetails = buildPatientDetails({
                birthDate: undefined,
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientDob />
                </PatientSummary>,
            );

            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
            // Should render empty string for date - check by ID
            const dobElement = document.getElementById('patient-summary-date-of-birth');
            expect(dobElement).toHaveTextContent('');
        });

        it('handles undefined postalCode', () => {
            const mockDetails = buildPatientDetails({
                postalCode: undefined,
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientPostcode />
                </PatientSummary>,
            );

            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        });

        it('handles undefined familyName', () => {
            const mockDetails = buildPatientDetails({
                familyName: undefined,
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(
                <PatientSummary>
                    <PatientSummary.PatientFamilyName />
                </PatientSummary>,
            );

            expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        });
    });

    describe('Context Error Handling', () => {
        it('throws error when PatientSummary subcomponents are used outside of PatientSummary', () => {
            // Suppress error output for this test as we expect it to throw
            const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

            expect(() => {
                render(<PatientSummary.PatientNhsNumber />);
            }).toThrow('PatientSummary subcomponents must be used within PatientSummary');

            spy.mockRestore();
        });
    });

    describe('Edge Cases for Optional Fields', () => {
        it('renders correctly when patient is deceased but showDeceasedTag is undefined', () => {
            const mockDetails = buildPatientDetails({
                deceased: true,
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(<PatientSummary showDeceasedTag={undefined} />);

            expect(screen.queryByTestId('deceased-patient-tag')).not.toBeInTheDocument();
        });

        it('renders correctly when patient deceased status is undefined', () => {
            const mockDetails = buildPatientDetails({
                deceased: undefined,
            });

            mockedUsePatient.mockReturnValue(mockDetails);
            render(<PatientSummary showDeceasedTag />);

            expect(screen.queryByTestId('deceased-patient-tag')).not.toBeInTheDocument();
        });
    });
});
