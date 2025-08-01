import { render, screen, waitFor } from '@testing-library/react';
import {
    UploadDocument,
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
} from '../../../../types/pages/UploadDocumentsPage/types';
import DocumentUploadLloydGeorgePreview from './DocumentUploadLloydGeorgePreview';

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

// Mock PDF merger
const mockAdd = vi.fn();
const mockSetMetadata = vi.fn();
const mockSaveAsBlob = vi.fn();

vi.mock('pdf-merger-js/browser', () => ({
    default: vi.fn(() => ({
        add: mockAdd,
        setMetadata: mockSetMetadata,
        saveAsBlob: mockSaveAsBlob,
    })),
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

        // Reset mocks
        mockAdd.mockClear().mockResolvedValue(undefined);
        mockSetMetadata.mockClear().mockResolvedValue(undefined);
        mockSaveAsBlob
            .mockClear()
            .mockResolvedValue(new Blob(['test'], { type: 'application/pdf' }));
        URL.createObjectURL = vi.fn().mockReturnValue('blob:test-url');
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
            mockSaveAsBlob.mockResolvedValue(mockBlob);

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
