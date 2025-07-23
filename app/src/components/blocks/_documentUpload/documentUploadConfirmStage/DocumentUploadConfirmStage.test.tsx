import { render, waitFor, screen } from '@testing-library/react';
import DocumentUploadConfirmStage from './DocumentUploadConfirmStage';
import { DOCUMENT_TYPE, UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import DocumentSelectStage from '../documentSelectStage/DocumentSelectStage';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

const patientDetails = buildPatientDetails();

URL.createObjectURL = vi.fn();

describe('DocumentUploadCompleteStage', () => {
    let documents: UploadDocument[];
    beforeEach(() => {
        vi.mocked(usePatient).mockReturnValue(patientDetails);

        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        documents = [];
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders', async () => {
            renderSut(documents);

            await waitFor(async () => {
                expect(screen.getByText('Check your files before uploading')).toBeInTheDocument();
            });
        });

        it('renders patient summary fields is inset', async () => {
            renderSut(documents);

            const insetText = screen
                .getByText('Make sure that all files uploaded are for this patient only:')
                .closest('.nhsuk-inset-text');
            expect(insetText).toBeInTheDocument();

            const expectedFullName = `${patientDetails.familyName}, ${patientDetails.givenName}`;
            expect(screen.getByText(/Patient name/i)).toBeInTheDocument();
            expect(screen.getByText(expectedFullName)).toBeInTheDocument();

            expect(screen.getByText(/NHS number/i)).toBeInTheDocument();
            const expectedNhsNumber = formatNhsNumber(patientDetails.nhsNumber);
            expect(screen.getByText(expectedNhsNumber)).toBeInTheDocument();

            expect(screen.getByText(/Date of birth/i)).toBeInTheDocument();
            const expectedDob = getFormattedDate(new Date(patientDetails.birthDate));
            expect(screen.getByText(expectedDob)).toBeInTheDocument();
        });
    });
});

function renderSut(documents: UploadDocument[]) {
    render(
        <DocumentUploadConfirmStage documents={documents} startUpload={() => Promise.resolve()} />,
    );
}
