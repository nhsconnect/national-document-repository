import usePatient from '../../../../helpers/hooks/usePatient';
import {
    buildDocument,
    buildPatientDetails,
    buildTextFile,
} from '../../../../helpers/test/testBuilders';
import { act, render, screen, waitFor } from '@testing-library/react';
import LloydGeorgeUploadComplete from './LloydGeorgeUploadCompleteStage';
import { DOCUMENT_UPLOAD_STATE as documentUploadStates } from '../../../../types/pages/UploadDocumentsPage/types';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';

jest.mock('../../../../helpers/hooks/usePatient');
const mockedUsePatient = usePatient as jest.Mock;
const mockPatient = buildPatientDetails();

jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
const mockedUseNavigate = jest.fn();

describe('LloydGeorgeUploadComplete', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the card component with patient details', () => {
        const dateToday = getFormattedDate(new Date());

        render(<LloydGeorgeUploadComplete documents={[]} />);

        expect(screen.getByRole('heading', { name: 'Record uploaded for' })).toBeInTheDocument();
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('NHS number: 900 000 0009')).toBeInTheDocument();
        expect(screen.getByText(`Date uploaded: ${dateToday}`)).toBeInTheDocument();
        expect(
            screen.queryByTestId('View successfully uploaded documents'),
        ).not.toBeInTheDocument();
    });

    it('renders the successfully uploaded files section', async () => {
        const mockDocuments = [
            buildDocument(buildTextFile('test1'), documentUploadStates.SUCCEEDED),
            buildDocument(buildTextFile('test2'), documentUploadStates.SUCCEEDED),
        ];

        render(<LloydGeorgeUploadComplete documents={mockDocuments} />);

        expect(screen.getByText('You have successfully uploaded 2 files')).toBeInTheDocument();
        expect(screen.getByText('Hide files')).toBeInTheDocument();
        expect(screen.getByText('test1.txt')).toBeInTheDocument();
        expect(screen.getByText('test2.txt')).toBeInTheDocument();

        expect(screen.queryByText('View files')).not.toBeInTheDocument();

        act(() => {
            userEvent.click(screen.getByText('Hide files'));
        });

        await waitFor(() => {
            expect(screen.getByText('View files')).toBeInTheDocument();
        });

        expect(screen.queryByText('Hide files')).not.toBeInTheDocument();
        expect(screen.queryByText('test1.txt')).not.toBeVisible();
        expect(screen.queryByText('test2.txt')).not.toBeVisible();
    });

    it('renders the "What happens next" section and both buttons', () => {
        render(<LloydGeorgeUploadComplete documents={[]} />);

        expect(screen.getByText('What happens next')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'View record' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Search for a patient' })).toBeInTheDocument();
    });

    it('pass accessibility checks', async () => {
        const mockDocuments = [
            buildDocument(buildTextFile('test1'), documentUploadStates.SUCCEEDED),
            buildDocument(buildTextFile('test2'), documentUploadStates.SUCCEEDED),
        ];

        render(<LloydGeorgeUploadComplete documents={mockDocuments} />);

        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });

    it('navigates to LG record page when "View record" button is clicked', async () => {
        render(<LloydGeorgeUploadComplete documents={[]} />);

        act(() => {
            userEvent.click(screen.getByRole('button', { name: 'View record' }));
        });

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.LLOYD_GEORGE);
        });
    });

    it('navigates to patient search page when "Search for a patient" button is clicked', async () => {
        render(<LloydGeorgeUploadComplete documents={[]} />);

        act(() => {
            userEvent.click(screen.getByRole('button', { name: 'Search for a patient' }));
        });

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SEARCH_PATIENT);
        });
    });
});
