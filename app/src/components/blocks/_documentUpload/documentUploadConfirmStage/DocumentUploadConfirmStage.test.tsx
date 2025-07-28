import { render, waitFor, screen } from '@testing-library/react';
import DocumentUploadConfirmStage from './DocumentUploadConfirmStage';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import * as ReactRouter from 'react-router-dom';
import { MemoryHistory, createMemoryHistory } from 'history';
import userEvent from '@testing-library/user-event';
import { routes } from '../../../../types/generic/routes';

const mockedUseNavigate = vi.fn();
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockedUseNavigate,
    };
});

URL.createObjectURL = vi.fn();

let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('DocumentUploadCompleteStage', () => {
    const mockStartUpload = vi.fn();

    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
        history = createMemoryHistory({ initialEntries: ['/'], initialIndex: 0 });
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders', async () => {
        renderApp(history, 1);

        await waitFor(async () => {
            expect(screen.getByText('Check your files before uploading')).toBeInTheDocument();
        });
    });

    it('should trigger start upload when confirm button is clicked', async () => {
        renderApp(history, 1);

        userEvent.click(await screen.findByTestId('confirm-button'));

        await waitFor(() => {
            expect(mockStartUpload).toHaveBeenCalled();
        });
    });

    it('should render pagination when doc count is high enough', async () => {
        renderApp(history, 15);

        await waitFor(async () => {
            expect(await screen.findByTestId('page-1-button')).toBeInTheDocument();
            expect(await screen.findByTestId('page-2-button')).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('should navigate to previous screen when go back is clicked', async () => {
            renderApp(history, 1);

            userEvent.click(await screen.findByTestId('go-back-link'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(-1);
            });
        });

        it('should navigate to the file selection page when change files is clicked', async () => {
            renderApp(history, 1);

            userEvent.click(await screen.findByTestId('change-files-button'));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.DOCUMENT_UPLOAD);
            });
        });
    });

    const renderApp = (history: MemoryHistory, docsLength: number) => {
        const documents: UploadDocument[] = [];
        for (let i = 1; i <= docsLength; i++) {
            documents.push({
                attempts: 0,
                id: `${i}`,
                docType: DOCUMENT_TYPE.LLOYD_GEORGE,
                file: new File(['file'], `file ${i}.pdf`),
                state: DOCUMENT_UPLOAD_STATE.SELECTED,
            });
        }

        return render(
            <ReactRouter.Router navigator={history} location={history.location}>
                <DocumentUploadConfirmStage documents={documents} startUpload={mockStartUpload} />
            </ReactRouter.Router>,
        );
    };
});
