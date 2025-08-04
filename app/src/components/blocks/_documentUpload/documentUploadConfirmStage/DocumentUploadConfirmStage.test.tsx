import { render, waitFor, screen } from '@testing-library/react';
import DocumentUploadConfirmStage from './DocumentUploadConfirmStage';
import { UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

URL.createObjectURL = vi.fn();

describe('DocumentUploadCompleteStage', () => {
    let documents: UploadDocument[];
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        documents = [];
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders', async () => {
            render(
                <DocumentUploadConfirmStage
                    documents={documents}
                    startUpload={() => Promise.resolve()}
                />,
            );

            await waitFor(async () => {
                expect(screen.getByText('Check your files before uploading')).toBeInTheDocument();
            });
        });
    });
});
