// need to use happy-dom for this test file as jsdom doesn't support DOMMatrix https://github.com/jsdom/jsdom/issues/2647
// @vitest-environment happy-dom
import { render, waitFor, screen } from '@testing-library/react';
import { DOCUMENT_TYPE, UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import DocumentSelectStage from './DocumentSelectStage';

const mockNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

URL.createObjectURL = vi.fn();

describe('DocumentSelectStage', () => {
    let documents: UploadDocument[] = [];
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
                <DocumentSelectStage
                    documents={documents}
                    setDocuments={() => {}}
                    documentType={DOCUMENT_TYPE.LLOYD_GEORGE}
                />,
            );

            await waitFor(async () => {
                expect(
                    screen.getByText(
                        'Make sure that all files uploaded are for this patient only.',
                    ),
                ).toBeInTheDocument();
            });
        });
    });
});
