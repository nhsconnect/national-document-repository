import { render, waitFor, screen } from '@testing-library/react';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import DocumentUploadingStage from './DocumentUploadingStage';
import { buildLgFile } from '../../../../helpers/test/testBuilders';
import { MemoryRouter } from 'react-router-dom';
import { routes } from '../../../../types/generic/routes';

const mockStartUpload = vi.fn();
const mockedNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockedNavigate,
    };
});

URL.createObjectURL = vi.fn();

describe('DocumentUploadCompleteStage', () => {
    let documents: UploadDocument[];

    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        documents = [
            {
                docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                id: '1',
                file: buildLgFile(1),
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
        it('renders', async () => {
            renderApp(documents);

            await waitFor(async () => {
                expect(
                    screen.queryAllByText('Your documents are uploading')[0],
                ).toBeInTheDocument();
            });
        });

        it('should trigger start upload when page is loaded', async () => {
            renderApp(documents);

            await waitFor(() => {
                expect(mockStartUpload).toHaveBeenCalledTimes(1);
            });
        });
    });

    it('should navigate to home if there are no documents to upload', async () => {
        documents[0].state = DOCUMENT_UPLOAD_STATE.SUCCEEDED;
        renderApp(documents);

        await waitFor(() => {
            expect(mockedNavigate).toHaveBeenCalledWith(routes.HOME);
        });
    });

    const renderApp = (documents: UploadDocument[]) => {
        render(
            <MemoryRouter>
                <DocumentUploadingStage documents={documents} startUpload={mockStartUpload} />
            </MemoryRouter>,
        );
    };
});
