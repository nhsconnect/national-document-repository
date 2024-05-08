import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import PatientDetails from './PatientDetails';
import { render, screen } from '@testing-library/react';

jest.mock('../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as jest.Mock;

describe('PatientDetails', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders provided patient information', () => {
        const mockDetails = buildPatientDetails({
            familyName: 'Jones',
            nhsNumber: '0000222000',
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientDetails />);

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

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<PatientDetails />);

        // Using hard coded expected value instead of duplicating the expected logic
        const expectedGivenName = 'Comfort Zulu';
        expect(screen.getByText(expectedGivenName)).toBeInTheDocument();
    });
});
