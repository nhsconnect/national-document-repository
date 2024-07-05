import { createMemoryHistory } from 'history';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DocumentSearchResultsOptions from './DocumentSearchResultsOptions';
import { SUBMISSION_STATE } from '../../../../types/pages/documentSearchResultsPage/types';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { buildPatientDetails } from '../../../../helpers/test/testBuilders';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import getPresignedUrlForZip from '../../../../helpers/requests/getPresignedUrlForZip';
import waitForSeconds from '../../../../helpers/utils/waitForSeconds';

jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../../../helpers/requests/getPresignedUrlForZip');
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});

const mockedUseNavigate = jest.fn();
const mockGetPresignedUrlForZip = getPresignedUrlForZip as jest.MockedFunction<
    typeof getPresignedUrlForZip
>;
const updateDownloadState = jest.fn();

describe('DocumentSearchResultsOptions', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        // window.HTMLAnchorElement.prototype.click = jest.fn();
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
            // suppress warning msg of <a> element being clicked when downloading zip file
            window.HTMLAnchorElement.prototype.click = jest.fn();

            mockGetPresignedUrlForZip.mockResolvedValue('test-presigned-url');

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
            // To delay the mock request, and give a chance for the spinner to appear
            window.HTMLAnchorElement.prototype.click = jest.fn();
            mockGetPresignedUrlForZip.mockImplementation(() =>
                waitForSeconds(0.5).then(() => 'test-presigned-url'),
            );

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
                expect(
                    screen.getByRole('button', { name: 'Downloading documents' }),
                ).toBeInTheDocument();
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
            mockGetPresignedUrlForZip.mockImplementation(() => Promise.reject(errorResponse));

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
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routeChildren.ARF_DELETE_CONFIRMATION,
                );
            });
        });
    });

    describe('Accessibility', () => {
        it('pass accessibility checks at page entry point', async () => {
            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);

            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });

        it('pass accessibility checks when download was successful', async () => {
            renderDocumentSearchResultsOptions(SUBMISSION_STATE.SUCCEEDED);

            await screen.findByText('All documents have been successfully downloaded.');
            const results = await runAxeTest(document.body);
            expect(results).toHaveNoViolations();
        });
    });

    describe('Navigation', () => {
        it('navigates to session expire page when API returns 403', async () => {
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
            mockGetPresignedUrlForZip.mockImplementation(() => Promise.reject(errorResponse));

            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);

            expect(history.location.pathname).toBe('/example');

            userEvent.click(screen.getByRole('button', { name: 'Download All Documents' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });
        it('navigates to error page when API returns 5XX', async () => {
            const errorResponse = {
                response: {
                    status: 500,
                    data: { message: 'Server error', err_code: 'SP_1001' },
                },
            };
            mockGetPresignedUrlForZip.mockImplementation(() => Promise.reject(errorResponse));

            renderDocumentSearchResultsOptions(SUBMISSION_STATE.INITIAL);
            userEvent.click(screen.getByRole('button', { name: 'Download All Documents' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
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
        />,
    );
};
