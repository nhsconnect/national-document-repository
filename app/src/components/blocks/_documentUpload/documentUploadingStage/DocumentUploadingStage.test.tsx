import { render, waitFor, screen } from '@testing-library/react';
import { UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import DocumentUploadingStage from './DocumentUploadingStage';

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

URL.createObjectURL = vi.fn();

describe('DocumentUploadCompleteStage', () => {
    let documents: UploadDocument[];
    const mockStartUpload = vi.fn();
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        documents = [];
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders', async () => {
            render(<DocumentUploadingStage documents={documents} startUpload={mockStartUpload} />);

            await waitFor(async () => {
                expect(
                    screen.queryAllByText('Your documents are uploading')[0],
                ).toBeInTheDocument();
            });
        });

        it('should trigger start upload when page is loaded', async () => {
            render(<DocumentUploadingStage documents={documents} startUpload={mockStartUpload} />);
    
            await waitFor(() => {
                expect(mockStartUpload).toHaveBeenCalledTimes(1);
            });
        });
    });
});
