import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { render, screen } from '@testing-library/react';
import ReducedPatientInfo from './ReducedPatientInfo';

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
        const mockDetails = buildPatientDetails();
        mockedUsePatient.mockReturnValue(mockDetails);

        render(<ReducedPatientInfo />);

        expect(screen.getByText('NHS number: 900 000 0009')).toBeInTheDocument();
        expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    it('renders multiple given names with correct spacing', () => {
        const mockDetails = buildPatientDetails({
            familyName: 'Jones',
            givenName: ['Comfort', 'Zulu'],
        });

        mockedUsePatient.mockReturnValue(mockDetails);
        render(<ReducedPatientInfo />);

        // Using hard coded expected value instead of duplicating the expected logic
        const expectedName = 'Comfort Zulu Jones';
        expect(screen.getByText(expectedName)).toBeInTheDocument();
    });
});
