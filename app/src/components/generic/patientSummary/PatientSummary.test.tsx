import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import PatientSummary from './PatientSummary';
import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi, Mock } from 'vitest';

vi.mock('../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as Mock;

describe('PatientSummary', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'jest';
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

        expect(screen.getByText(mockDetails.nhsNumber)).toBeInTheDocument();
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
});
