import { render, waitFor, screen } from '@testing-library/react';
import { DOCUMENT_TYPE, UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import DocumentUploadRemoveFilesStage from './DocumentUploadRemoveFilesStage';

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
                <DocumentUploadRemoveFilesStage
                    documents={documents}
                    setDocuments={() => {}}
                    documentType={DOCUMENT_TYPE.LLOYD_GEORGE}
                />,
            );

            await waitFor(async () => {
                expect(
                    screen.getByText('Are you sure you want to remove all selected files?'),
                ).toBeInTheDocument();
            });
        });
    });
});
