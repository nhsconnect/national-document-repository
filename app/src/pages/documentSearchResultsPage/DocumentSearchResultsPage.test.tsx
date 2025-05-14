import { act, render, screen, waitFor } from '@testing-library/react';
import DocumentSearchResultsPage from './DocumentSearchResultsPage';
import userEvent from '@testing-library/user-event';
import { buildPatientDetails, buildSearchResult } from '../../helpers/test/testBuilders';
import { routes } from '../../types/generic/routes';
import axios from 'axios';
import usePatient from '../../helpers/hooks/usePatient';
import * as ReactRouter from 'react-router-dom';
import { History, createMemoryHistory } from 'history';
import { runAxeTest } from '../../helpers/test/axeTestHelper';
import { afterEach, beforeEach, describe, expect, it, vi, Mock, Mocked } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', async () => ({
    ...(await vi.importActual('react-router-dom')),
    useNavigate: () => mockedUseNavigate,
    Link: (props: ReactRouter.LinkProps) => <a {...props} role="link" />,
}));

vi.mock('axios');
Date.now = () => new Date('2020-01-01T00:00:00.000Z').getTime();
vi.mock('../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../helpers/hooks/usePatient');
vi.mock('../../helpers/hooks/useConfig');

const mockedAxios = axios as Mocked<typeof axios>;
const mockedUsePatient = usePatient as Mock;
const mockPatient = buildPatientDetails();

let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('<DocumentSearchResultsPage />', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });

        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the page after a successful response from api', async () => {
            mockedAxios.get.mockResolvedValue(async () => {
                return Promise.resolve({ data: [buildSearchResult()] });
            });

            renderPage(history);

            expect(
                screen.getByRole('heading', {
                    name: 'Manage this Lloyd George record',
                }),
            ).toBeInTheDocument();

            await waitFor(() => {
                expect(
                    screen.queryByRole('progressbar', { name: 'Loading...' }),
                ).not.toBeInTheDocument();
            });
        });

        it('displays a progress bar when the document search results are being requested', async () => {
            mockedAxios.get.mockImplementation(async () => {
                await new Promise((resolve) => {
                    setTimeout(() => {
                        // To delay the mock request, and give a chance for the progress bar to appear
                        resolve(null);
                    }, 500);
                });
                return Promise.resolve({ data: [buildSearchResult()] });
            });

            renderPage(history);

            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
        });

        it('displays a message when a document search returns no results', async () => {
            mockedAxios.get.mockResolvedValue(async () => {
                return Promise.resolve({ data: [] });
            });

            renderPage(history);

            await waitFor(() => {
                expect(
                    screen.getByText('There are no documents available for this patient.'),
                ).toBeInTheDocument();
            });

            expect(
                screen.queryByRole('button', { name: 'Download all documents' }),
            ).not.toBeInTheDocument();
            expect(screen.queryByTestId('delete-all-documents-btn')).not.toBeInTheDocument();
        });

        it('displays a error messages when the call to document manifest fails', async () => {
            mockedAxios.get.mockResolvedValue({ data: [buildSearchResult()] });

            const errorResponse = {
                response: {
                    status: 403,
                    message: 'An error occurred',
                },
            };

            renderPage(history);

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            await waitFor(() => {
                screen.getByRole('button', { name: 'Download all documents' });
            });
            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Download all documents' }));
            });

            expect(
                await screen.findByText('An error has occurred while preparing your download'),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Download all documents' }),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Remove all documents' }),
            ).toBeInTheDocument();
        });

        it('displays a error messages when the call to document manifest return 400', async () => {
            mockedAxios.get.mockResolvedValue({ data: [buildSearchResult()] });

            const errorResponse = {
                response: {
                    status: 400,
                    data: { message: 'An error occurred', err_code: 'SP_1001' },
                },
            };

            renderPage(history);

            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            await waitFor(() => {
                screen.getByRole('button', { name: 'Download all documents' });
            });
            act(() => {
                userEvent.click(screen.getByRole('button', { name: 'Download all documents' }));
            });
            expect(
                await screen.findByText('An error has occurred while preparing your download'),
            ).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Download all documents' }),
            ).toBeInTheDocument();
            expect(screen.getByTestId('delete-all-documents-btn')).toBeInTheDocument();
        });

        it('displays a message when a document search return 423 locked error', async () => {
            const errorResponse = {
                response: {
                    status: 423,
                    message: 'An error occurred',
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPage(history);

            expect(
                await screen.findByText(
                    'There are already files being uploaded for this patient, please try again in a few minutes.',
                ),
            ).toBeInTheDocument();
        });
    });

    describe.skip('Accessibility', () => {
        it('pass accessibility checks at loading screen', async () => {
            mockedAxios.get.mockReturnValueOnce(
                new Promise((resolve) => setTimeout(resolve, 100000)),
            );
            renderPage(history);

            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when displaying search result', async () => {
            mockedAxios.get.mockResolvedValue({ data: [buildSearchResult()] });

            renderPage(history);

            expect(await screen.findByText('List of documents available')).toBeInTheDocument();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when error boxes are showing up', async () => {
            mockedAxios.get.mockResolvedValue({ data: [buildSearchResult()] });
            const errorResponse = {
                response: {
                    status: 400,
                    data: { message: 'An error occurred', err_code: 'SP_1001' },
                },
            };
            renderPage(history);

            const downloadButton = await screen.findByRole('button', {
                name: 'Download all documents',
            });
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));
            act(() => {
                userEvent.click(downloadButton);
            });

            expect(
                await screen.findByText('Sorry, the service is currently unavailable.'),
            ).toBeInTheDocument();
            expect(
                await screen.findByText('An error has occurred while preparing your download'),
            ).toBeInTheDocument();

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates to Error page when call to doc manifest return 500', async () => {
            mockedAxios.get.mockResolvedValue({ data: [buildSearchResult()] });
            const errorResponse = {
                response: {
                    status: 500,
                    data: { message: 'An error occurred', err_code: 'SP_1001' },
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            act(() => {
                renderPage(history);
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
                );
            });
        });
        it('navigates to session expire page when a document search return 403 unauthorised error', async () => {
            const errorResponse = {
                response: {
                    status: 403,
                    message: 'An error occurred',
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderPage(history);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });
    });

    const renderPage = (history: History) => {
        return render(
            <ReactRouter.Router navigator={history} location={history.location}>
                <DocumentSearchResultsPage />
            </ReactRouter.Router>,
        );
    };
});
