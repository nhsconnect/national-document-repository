import { createMemoryHistory } from 'history';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import DocumentSearchResultsOptions from './DocumentSearchResultsOptions';
import { SUBMISSION_STATE } from '../../../types/pages/documentSearchResultsPage/types';
import { routes } from '../../../types/generic/routes';
import { buildPatientDetails } from '../../../helpers/test/testBuilders';

const mockedUseNavigate = jest.fn();
jest.mock('../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../helpers/hooks/useBaseAPIUrl');
jest.mock('axios');
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
const mockedAxios = axios as jest.Mocked<typeof axios>;
const updateDownloadState = jest.fn();
const mockSetIsDeletingDocuments = jest.fn();

describe('DocumentSearchResultsOptions', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the components on initial state', async () => {
            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);

            expect(
                screen.getByText(
                    'Only permanently delete all documents for this patient if you have a valid reason to. For example, if the retention period of these documents has been reached.',
                ),
            ).toBeInTheDocument();

            expect(
                screen.getByRole('button', { name: 'Download All Documents' }),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Delete All Documents' }),
            ).toBeInTheDocument();
        });

        it('calls parent callback function to pass successful state after a successful response from api', async () => {
            mockedAxios.get.mockResolvedValue(async () => {
                return Promise.resolve({ data: 'test-presigned-url' });
            });

            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);
            userEvent.click(await screen.findByRole('button', { name: 'Download All Documents' }));
            await waitFor(() => {
                expect(updateDownloadState).toHaveBeenCalledWith(SUBMISSION_STATE.SUCCEEDED);
            });
        });

        it('renders success message when the download state is successful', async () => {
            renderDocumentSearchResultsOptions(SUBMISSION_STATE.SUCCEEDED);
            expect(
                screen.getByText('All documents have been successfully downloaded.'),
            ).toBeInTheDocument();
        });

        it('calls parent callback function to pass pending state when waiting for response from api', async () => {
            mockedAxios.get.mockImplementation(async () => {
                await new Promise((resolve) => {
                    setTimeout(() => {
                        // To delay the mock request, and give a chance for the spinner to appear
                        resolve(null);
                    }, 500);
                });
                return Promise.resolve({ data: 'test-presigned-url' });
            });

            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);

            expect(
                screen.getByRole('button', { name: 'Download All Documents' }),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Delete All Documents' }),
            ).toBeInTheDocument();

            userEvent.click(screen.getByRole('button', { name: 'Download All Documents' }));

            expect(updateDownloadState).toHaveBeenCalledWith(SUBMISSION_STATE.PENDING);
        });

        it('renders the download spinner when download state is pending', async () => {
            renderDocumentSearchResultsOptions(SUBMISSION_STATE.PENDING);

            await waitFor(() => {
                expect(screen.getByRole('SpinnerButton')).toBeInTheDocument();
            });

            expect(
                screen.queryByRole('button', { name: 'Download All Documents' }),
            ).not.toBeInTheDocument();
        });

        it('calls parent callback function to pass failed state when API returns 4xx', async () => {
            const errorResponse = {
                response: {
                    status: 400,
                    data: { message: 'Error', err_code: 'SP_1001' },
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);

            userEvent.click(screen.getByRole('button', { name: 'Download All Documents' }));

            await waitFor(() => {
                expect(updateDownloadState).toHaveBeenCalledWith(SUBMISSION_STATE.FAILED);
            });
        });

        it('calls delete all documents function when Delete button is clicked', async () => {
            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);

            userEvent.click(screen.getByRole('button', { name: 'Delete All Documents' }));

            await waitFor(() => {
                expect(mockSetIsDeletingDocuments).toHaveBeenCalledWith(true);
            });
        });
    });

    describe('Navigation', () => {
        it('navigates to home page when API returns 403', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });

            const errorResponse = {
                response: {
                    status: 403,
                    message: 'Forbidden',
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);

            expect(history.location.pathname).toBe('/example');

            userEvent.click(screen.getByRole('button', { name: 'Download All Documents' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.START);
            });
        });
        it('navigates to error page when API returns 5XX', async () => {
            const errorResponse = {
                response: {
                    status: 500,
                    data: { message: 'Server error', err_code: 'SP_1001' },
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);
            userEvent.click(screen.getByRole('button', { name: 'Download All Documents' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routes.SERVER_ERROR + '?errorCode=SP_1001',
                );
            });
        });
    });
});

const renderDocumentSearchResultsOptions = (downloadState: SUBMISSION_STATE) => {
    const patient = buildPatientDetails();
    render(
        <DocumentSearchResultsOptions
            nhsNumber={patient.nhsNumber}
            downloadState={downloadState}
            updateDownloadState={updateDownloadState}
            numberOfFiles={7}
            setIsDeletingDocuments={mockSetIsDeletingDocuments}
        />,
    );
};
