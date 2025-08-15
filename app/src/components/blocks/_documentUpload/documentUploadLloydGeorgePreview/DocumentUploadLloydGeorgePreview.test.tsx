import { render, screen, waitFor } from '@testing-library/react';
import {
    UploadDocument,
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
} from '../../../../types/pages/UploadDocumentsPage/types';
import DocumentUploadLloydGeorgePreview from './DocumentUploadLloydGeorgePreview';
import getMergedPdfBlob from '../../../../helpers/utils/pdfMerger';

const mockNavigate = vi.fn();

vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('../../../../helpers/utils/pdfMerger');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

URL.createObjectURL = vi.fn();

const createMockDocument = (id: string): UploadDocument => ({
    state: DOCUMENT_UPLOAD_STATE.SELECTED,
    file: new File(['test'], 'test.pdf', { type: 'application/pdf' }),
    id,
    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
    attempts: 0,
});

describe('DocumentUploadCompleteStage', () => {
    let documents: UploadDocument[];
    const mockSetMergedPdfBlob = vi.fn();

    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        documents = [];
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders without documents', () => {
            render(
                <DocumentUploadLloydGeorgePreview
                    documents={documents}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            // When no documents are provided, nothing should render
            expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
        });

        it('renders PdfViewer when documents are provided and merged', async () => {
            const testDocuments = [createMockDocument('1'), createMockDocument('2')];

            render(
                <DocumentUploadLloydGeorgePreview
                    documents={testDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            // Wait for the PDF merger to complete and the PdfViewer to render
            await waitFor(() => {
                expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
            });
        });

        it('calls setMergedPdfBlob with the merged PDF blob', async () => {
            const testDocuments = [createMockDocument('1')];
            const mockBlob = new Blob(['test pdf content'], { type: 'application/pdf' });
            vi.mocked(getMergedPdfBlob).mockResolvedValue(mockBlob);

            render(
                <DocumentUploadLloydGeorgePreview
                    documents={testDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            // Wait for the PDF merger to complete
            await waitFor(() => {
                expect(mockSetMergedPdfBlob).toHaveBeenCalledWith(mockBlob);
            });
        });
    });
});
