import usePatient from '../../../helpers/hooks/usePatient';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import PatientSummary from './PatientSummary';
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
            screen.getByText(`${mockDetails.givenName[0]} ${mockDetails.familyName}`),
        ).toBeInTheDocument();
    });
});
