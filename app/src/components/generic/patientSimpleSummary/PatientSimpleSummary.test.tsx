import React from 'react';
import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import PatientSimpleSummary from './PatientSimpleSummary';
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
    const mockDetails = buildPatientDetails({
        familyName: 'Jones',
        givenName: ['John'],
        nhsNumber: '0000222000',
        birthDate: '1970-01-01',
    });

    const mockLongName = buildPatientDetails({
        familyName: 'AVeryLongFirstName',
        givenName: ['AVeryLongSecondName'],
        nhsNumber: '0000222000',
        birthDate: '1970-01-01',
    });

    it('renders provided patient information', () => {
        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSimpleSummary />);

        const nhsNumber = new RegExp(formatNhsNumber(mockDetails.nhsNumber.toString()), 'i');
        const dob = new RegExp(getFormattedDate(new Date(mockDetails.birthDate)), 'i');

        expect(screen.getByText(nhsNumber)).toBeInTheDocument();
        expect(screen.getByText(dob)).toBeInTheDocument();
    });

    it('renders multiple given names with correct spacing', () => {
        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSimpleSummary />);

        expect(
            screen.getByText(`${mockDetails.givenName[0]}, ${mockDetails.familyName}`),
        ).toBeInTheDocument();
    });

    it('displays a newline after name for very long names', () => {
        mockedUsePatient.mockReturnValue(mockLongName);

        render(<PatientSimpleSummary />);

        const patientInfo = screen.getByTestId('patient-info');

        expect(patientInfo.innerHTML).toContain('<br>');
    });

    it('displays patient details on same line for short names', () => {
        mockedUsePatient.mockReturnValue(mockDetails);

        render(<PatientSimpleSummary />);

        const patientInfo = screen.getByTestId('patient-info');

        expect(patientInfo.innerHTML).not.toContain('<br>');
    });

    it('renders deceased patient tag for a deceased patient when tag is enabled', () => {
        const mockDetails = buildPatientDetails({
            deceased: true,
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSimpleSummary showDeceasedTag />);

        expect(screen.getByTestId('deceased-patient-tag')).toBeInTheDocument();
    });

    it('does not render deceased patient tag for a deceased patient when tag is disabled', () => {
        const mockDetails = buildPatientDetails({
            deceased: true,
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSimpleSummary />);

        expect(screen.queryByTestId('deceased-patient-tag')).not.toBeInTheDocument();
    });

    it('does not render deceased patient tag for a none deceased patient when tag is enabled', () => {
        const mockDetails = buildPatientDetails({
            deceased: false,
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSimpleSummary />);

        expect(screen.queryByTestId('deceased-patient-tag')).not.toBeInTheDocument();
    });
});
