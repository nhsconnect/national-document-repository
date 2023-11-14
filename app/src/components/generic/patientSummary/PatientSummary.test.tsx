import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import PatientSummary from './PatientSummary';
import { render, screen } from '@testing-library/react';

describe('PatientSummary', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders provided patient information', () => {
        const mockDetails = buildPatientDetails({
            familyName: 'Jones',
            nhsNumber: '0000222000',
        });

        render(<PatientSummary patientDetails={mockDetails} />);

        expect(screen.getByText(mockDetails.nhsNumber)).toBeInTheDocument();
        expect(screen.getByText(mockDetails.familyName)).toBeInTheDocument();
        //expect(screen.getByText(mockDetails.givenName)).toBeInTheDocument()
    });

    it('renders multiple given names with correct spacing', () => {
        const mockDetails = buildPatientDetails({
            familyName: 'Jones',
            nhsNumber: '0000222000',
            givenName: ['Comfort', 'Zulu'],
        });

        render(<PatientSummary patientDetails={mockDetails} />);

        // Using hard coded expected value instead of duplicating the expected logic
        const expectedGivenName = 'Comfort Zulu';
        expect(screen.getByText(expectedGivenName)).toBeInTheDocument();
    });
});
