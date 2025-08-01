import { render, waitFor, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DocumentSelectOrderStage from './DocumentSelectOrderStage';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';

const mockNavigate = vi.fn();
const mockSetDocuments = vi.fn();
const mockSetMergedPdfBlob = vi.fn();

vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('../../../../helpers/hooks/useTitle');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

URL.createObjectURL = vi.fn(() => 'mocked-url');

// Mock scrollIntoView which is not available in JSDOM
Element.prototype.scrollIntoView = vi.fn();

vi.mock('../documentUploadLloydGeorgePreview/DocumentUploadLloydGeorgePreview', () => ({
    default: ({ documents }: { documents: UploadDocument[] }) => (
        <div data-testid="lloyd-george-preview">
            Lloyd George Preview for {documents.length} documents
        </div>
    ),
}));

describe('DocumentSelectOrderStage', () => {
    let documents: UploadDocument[] = [];

    const createMockFile = (name: string, id: string): File => {
        const file = new File(['content'], name, { type: 'application/pdf' });
        Object.defineProperty(file, 'name', { value: name, writable: false });
        return file;
    };

    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        documents = [
            {
                docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                id: '1',
                file: createMockFile('test-document-1.pdf', '1'),
                attempts: 0,
                state: DOCUMENT_UPLOAD_STATE.SELECTED,
                numPages: 5,
                position: 1,
            },
        ];
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the component with page title and instructions', async () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            await waitFor(() => {
                expect(
                    screen.getByText('What order do you want these files in?'),
                ).toBeInTheDocument();
                expect(
                    screen.getByText(
                        'If you have more than one file, they may not be in the correct order:',
                    ),
                ).toBeInTheDocument();
                expect(
                    screen.getByText(
                        'When you upload your files, they will be combined into a single PDF document.',
                    ),
                ).toBeInTheDocument();
            });
        });

        it('renders the document table with headers', () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            expect(screen.getByText('Filename')).toBeInTheDocument();
            expect(screen.getByText('Pages')).toBeInTheDocument();
            expect(screen.getByText('Position')).toBeInTheDocument();
            expect(screen.getByText('View file')).toBeInTheDocument();
            expect(screen.getByText('Remove file')).toBeInTheDocument();
        });

        it('displays document information in the table', () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            expect(screen.getByText('test-document-1.pdf')).toBeInTheDocument();
            expect(screen.getByText('5')).toBeInTheDocument();
            expect(screen.getByText('View')).toBeInTheDocument();
            expect(screen.getByText('Remove')).toBeInTheDocument();
        });

        it('renders continue button when documents are present', () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();
        });

        it('does not show "Remove all" button when there is only one document', () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            expect(screen.queryByText('Remove all')).not.toBeInTheDocument();
        });

        it('shows Lloyd George preview when documents contain Lloyd George type and form is valid', async () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            await waitFor(() => {
                expect(screen.getByText('Preview this Lloyd George record')).toBeInTheDocument();
                expect(screen.getByTestId('lloyd-george-preview')).toBeInTheDocument();
            });
        });

        it('shows message when no documents are present', () => {
            render(
                <DocumentSelectOrderStage
                    documents={[]}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            expect(screen.getByText(/You have removed all files/)).toBeInTheDocument();
            expect(screen.getByText('choose files')).toBeInTheDocument();
        });
    });

    describe('Position Selection', () => {
        it('renders position dropdown for each document', () => {
            const multipleDocuments = [
                ...documents,
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('test-document-2.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 2,
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={multipleDocuments}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            expect(screen.getByTestId('document-1-position')).toBeInTheDocument();
            expect(screen.getByTestId('document-2-position')).toBeInTheDocument();
        });

        it('updates document position when dropdown value changes', async () => {
            const user = userEvent.setup();
            const multipleDocuments = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 1,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('test-document-2.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 2,
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={multipleDocuments}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const positionSelect = screen.getByTestId('document-1-position');
            await user.selectOptions(positionSelect, '2');

            expect(mockSetDocuments).toHaveBeenCalled();
        });
    });

    describe('Document Removal', () => {
        it('calls onRemove when remove button is clicked', async () => {
            const user = userEvent.setup();

            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const removeButton = screen.getByRole('button', {
                name: /Remove test-document-1.pdf from selection/,
            });
            await user.click(removeButton);

            expect(mockSetDocuments).toHaveBeenCalledWith([]);
        });

        it('adjusts positions when removing a document from the middle of the list', async () => {
            const user = userEvent.setup();
            const multipleDocuments = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 1,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('test-document-2.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 2,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '3',
                    file: createMockFile('test-document-3.pdf', '3'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 2,
                    position: 3,
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={multipleDocuments}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            // Remove the middle document (position 2)
            const removeButton = screen.getByRole('button', {
                name: /Remove test-document-2.pdf from selection/,
            });
            await user.click(removeButton);

            // Verify that setDocuments was called with the correct updated list
            expect(mockSetDocuments).toHaveBeenCalledWith([
                expect.objectContaining({
                    id: '1',
                    position: 1, // Should remain unchanged
                }),
                expect.objectContaining({
                    id: '3',
                    position: 2, // Should be adjusted from 3 to 2
                }),
            ]);
        });

        it('removes document without affecting positions of documents with lower positions', async () => {
            const user = userEvent.setup();
            const multipleDocuments = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 1,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('test-document-2.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 2,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '3',
                    file: createMockFile('test-document-3.pdf', '3'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 2,
                    position: 3,
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={multipleDocuments}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            // Remove the last document (position 3)
            const removeButton = screen.getByRole('button', {
                name: /Remove test-document-3.pdf from selection/,
            });
            await user.click(removeButton);

            // Verify that documents with lower positions remain unchanged
            expect(mockSetDocuments).toHaveBeenCalledWith([
                expect.objectContaining({
                    id: '1',
                    position: 1, // Should remain unchanged
                }),
                expect.objectContaining({
                    id: '2',
                    position: 2, // Should remain unchanged
                }),
            ]);
        });

        it('handles removal of document without position set', async () => {
            const user = userEvent.setup();
            const documentsWithoutPosition = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: undefined, // No position set
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('test-document-2.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 1,
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={documentsWithoutPosition}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const removeButton = screen.getByRole('button', {
                name: /Remove test-document-1.pdf from selection/,
            });
            await user.click(removeButton);

            // Should remove the document and leave the other unchanged
            expect(mockSetDocuments).toHaveBeenCalledWith([
                expect.objectContaining({
                    id: '2',
                    position: 1,
                }),
            ]);
        });

        it('displays correct aria-label for each remove button', () => {
            const multipleDocuments = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('document-one.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 1,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('document-two.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 2,
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={multipleDocuments}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            expect(
                screen.getByRole('button', {
                    name: 'Remove document-one.pdf from selection',
                }),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', {
                    name: 'Remove document-two.pdf from selection',
                }),
            ).toBeInTheDocument();
        });

        it('shows appropriate message when all documents are removed', () => {
            render(
                <DocumentSelectOrderStage
                    documents={[]}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            expect(screen.getByText(/You have removed all files/)).toBeInTheDocument();
            expect(screen.getByText('choose files')).toBeInTheDocument();
        });
    });

    describe('Form Validation', () => {
        it('shows error when positions are not selected', async () => {
            const user = userEvent.setup();
            const documentsWithoutPositions = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 0, // Invalid position
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={documentsWithoutPositions}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const continueButton = screen.getByRole('button', { name: 'Continue' });
            await user.click(continueButton);

            await waitFor(() => {
                expect(
                    screen.getByText('Please select a position for every document'),
                ).toBeInTheDocument();
            });
        });

        it('shows error when duplicate positions are selected', async () => {
            const documentsWithDuplicatePositions = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 1,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('test-document-2.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 1, // Duplicate position
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={documentsWithDuplicatePositions}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            await waitFor(() => {
                expect(screen.getByText('There is a problem')).toBeInTheDocument();
            });
            expect(
                screen.getByText('Please ensure all documents have a unique position selected'),
            ).toBeInTheDocument();
        });

        it('shows error when duplicate positions are selected and continue is clicked', async () => {
            const user = userEvent.setup();
            const documentsWithDuplicatePositions = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 1,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('test-document-2.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 1, // Duplicate position
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={documentsWithDuplicatePositions}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const continueButton = screen.getByRole('button', { name: 'Continue' });
            await user.click(continueButton);

            await waitFor(() => {
                expect(screen.getByText('There is a problem')).toBeInTheDocument();
            });
            expect(
                screen.getByText('Please ensure all documents have a unique position selected'),
            ).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates to confirmation page when form is submitted successfully', async () => {
            const user = userEvent.setup();

            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const continueButton = screen.getByRole('button', { name: 'Continue' });
            await user.click(continueButton);

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith('/patient/document-upload/confirmation');
            });
        });

        it('navigates to document upload when "choose files" link is clicked', async () => {
            const user = userEvent.setup();

            render(
                <DocumentSelectOrderStage
                    documents={[]}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const chooseFilesButton = screen.getByRole('button', { name: 'choose files' });
            await user.click(chooseFilesButton);

            expect(mockNavigate).toHaveBeenCalledWith('/patient/document-upload');
        });
    });

    describe('File Preview', () => {
        it('creates object URL for file preview', () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const viewLink = screen.getByTestId('document-preview-1');
            expect(viewLink).toHaveAttribute('href', 'mocked-url');
            expect(global.URL.createObjectURL).toHaveBeenCalledWith(documents[0].file);
        });

        it('opens file preview in new tab', () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const viewLink = screen.getByTestId('document-preview-1');
            expect(viewLink).toHaveAttribute('target', '_blank');
            expect(viewLink).toHaveAttribute('rel', 'noreferrer');
        });
    });

    describe('PDF Viewer Integration', () => {
        it('renders PDF viewer when Lloyd George preview is shown', async () => {
            render(
                <DocumentSelectOrderStage
                    documents={documents}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            await waitFor(() => {
                expect(screen.getByTestId('lloyd-george-preview')).toBeInTheDocument();
            });
        });

        it('passes correct documents to Lloyd George preview component', async () => {
            const multipleDocuments = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 1,
                },
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '2',
                    file: createMockFile('test-document-2.pdf', '2'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 3,
                    position: 2,
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={multipleDocuments}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            await waitFor(() => {
                expect(
                    screen.getByText('Lloyd George Preview for 2 documents'),
                ).toBeInTheDocument();
            });
        });

        it('does not show PDF viewer when form has validation errors', async () => {
            const user = userEvent.setup();
            const documentsWithInvalidPositions = [
                {
                    docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                    id: '1',
                    file: createMockFile('test-document-1.pdf', '1'),
                    attempts: 0,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    numPages: 5,
                    position: 0, // Invalid position
                },
            ];

            render(
                <DocumentSelectOrderStage
                    documents={documentsWithInvalidPositions}
                    setDocuments={mockSetDocuments}
                    setMergedPdfBlob={mockSetMergedPdfBlob}
                />,
            );

            const continueButton = screen.getByRole('button', { name: 'Continue' });
            await user.click(continueButton);

            await waitFor(() => {
                expect(screen.queryByTestId('lloyd-george-preview')).not.toBeInTheDocument();
            });
        });
    });
});
