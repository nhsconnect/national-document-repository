import React from 'react';
import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import PatientSummary from './PatientSimpleSummary';
import { render, screen } from '@testing-library/react';

jest.mock('../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as jest.Mock;

describe('PatientSummary', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
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
        render(<PatientSummary />);

        const nhsNumber = new RegExp(formatNhsNumber(mockDetails.nhsNumber.toString()), 'i');
        const dob = new RegExp(getFormattedDate(new Date(mockDetails.birthDate)), 'i');

        expect(screen.getByText(nhsNumber)).toBeInTheDocument();
        expect(screen.getByText(dob)).toBeInTheDocument();
    });

    it('renders multiple given names with correct spacing', () => {
        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientSummary />);

        expect(
            screen.getByText(`${mockDetails.givenName[0]}, ${mockDetails.familyName}`),
        ).toBeInTheDocument();
    });

    it('displays a newline after name for very long names', () => {

        mockedUsePatient.mockReturnValue(mockLongName);

        render(<PatientSummary />);

        const patientInfo = screen.getByTestId('patient-info');

        expect(patientInfo.innerHTML).toContain('<br>');

    });

    it('displays patient details on same line for short names', () => {

        mockedUsePatient.mockReturnValue(mockDetails);

        render(<PatientSummary />);

        const patientInfo = screen.getByTestId('patient-info');

        expect(patientInfo.innerHTML).not.toContain('<br>');

    });

});
