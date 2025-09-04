import { render, waitFor, screen } from '@testing-library/react';
import DocumentUploadCompleteStage from './DocumentUploadCompleteStage';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';
import { LinkProps } from 'react-router-dom';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';
import usePatient from '../../../../helpers/hooks/usePatient';
import { getFormattedPatientFullName } from '../../../../helpers/utils/formatPatientFullName';

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));

URL.createObjectURL = vi.fn();

const patientDetails = buildPatientDetails();

describe('DocumentUploadCompleteStage', () => {
    beforeEach(() => {
        vi.mocked(usePatient).mockReturnValue(patientDetails);
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders', async () => {
        render(<DocumentUploadCompleteStage />);

        expect(
            screen.getByText('You have successfully uploaded a digital Lloyd George record for:'),
        ).toBeInTheDocument();

        const expectedFullName = getFormattedPatientFullName(patientDetails);
        expect(screen.getByTestId('patient-name').textContent).toEqual(
            'Patient name: ' + expectedFullName,
        );

        const expectedNhsNumber = formatNhsNumber(patientDetails.nhsNumber);
        expect(screen.getByTestId('nhs-number').textContent).toEqual(
            'NHS Number: ' + expectedNhsNumber,
        );

        const expectedDob = getFormattedDate(new Date(patientDetails.birthDate));
        expect(screen.getByTestId('dob').textContent).toEqual('Date of birth: ' + expectedDob);
    });

    it('should navigate to search when clicking the search link', async () => {
        render(<DocumentUploadCompleteStage />);

        await userEvent.click(screen.getByTestId('search-patient-link'));

        await waitFor(async () => {
            expect(mockNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
        });
    });

    it('should navigate to home when clicking the got to home button', async () => {
        render(<DocumentUploadCompleteStage />);

        await userEvent.click(screen.getByTestId('home-btn'));

        await waitFor(async () => {
            expect(mockNavigate).toHaveBeenCalledWith(routes.HOME);
        });
    });
});
