import { render, waitFor, screen } from "@testing-library/react";
import { UploadDocument } from "../../../../types/pages/UploadDocumentsPage/types";
import DocumentUploadLloydGeorgePreview from "./DocumentUploadLloydGeorgePreview";

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
            render(<DocumentUploadLloydGeorgePreview documents={documents} previewLoading={true} setMergedPdfBlob={() => {}} setPreviewLoading={() => {}} />);

            await waitFor(async () => {
                expect(
                    screen.getByText('Loading preview...')
                ).toBeInTheDocument();
            });
        });
    });
});