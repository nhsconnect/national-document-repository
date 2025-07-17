import { render, waitFor, screen } from "@testing-library/react";
import DocumentSelectOrderStage from "./DocumentSelectOrderStage";
import { DOCUMENT_TYPE, DOCUMENT_UPLOAD_STATE, UploadDocument } from "../../../../types/pages/UploadDocumentsPage/types";

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

URL.createObjectURL = vi.fn();

describe('DocumentSelectOrderStage', () => {
    let documents: UploadDocument[] = [];
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        documents = [{
            docType: DOCUMENT_TYPE.LLOYD_GEORGE, 
            id: '1', 
            file: new Blob() as File, 
            attempts: 0, 
            state: DOCUMENT_UPLOAD_STATE.SELECTED
        }];
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders', async () => {
            render(<DocumentSelectOrderStage documents={documents} setDocuments={() => {}} setMergedPdfBlob={() => {}} />);

            await waitFor(async () => {
                expect(
                    screen.getByText('Your files are not currently in order:')
                ).toBeInTheDocument();
            });
        });
    });
});