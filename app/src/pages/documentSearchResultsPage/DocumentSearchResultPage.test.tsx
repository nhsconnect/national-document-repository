import { render, screen, waitFor } from '@testing-library/react';
import PatientDetailsProvider from '../../providers/patientProvider/PatientProvider';
import DocumentSearchResultsPage from './DocumentSearchResultsPage';
import userEvent from '@testing-library/user-event';
import * as ReactRouter from 'react-router';
import { buildPatientDetails, buildSearchResult } from '../../helpers/test/testBuilders';
import { routes } from '../../types/generic/routes';
import { createMemoryHistory } from 'history';
import { PatientDetails } from '../../types/generic/patientDetails';
import axios from 'axios';

jest.mock('axios');

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('<DocumentSearchResultsPage />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the page after a successful response from api', async () => {
            mockedAxios.get.mockResolvedValue(async () => {
                return Promise.resolve({ data: [buildSearchResult()] });
            });

            renderSearchResultsPage();

            expect(
                screen.getByRole('heading', {
                    name: 'Download electronic health records and attachments',
                }),
            ).toBeInTheDocument();

            await waitFor(() => {
                expect(
                    screen.queryByRole('progressbar', { name: 'Loading...' }),
                ).not.toBeInTheDocument();
            });

            expect(screen.getByRole('link', { name: 'Start Again' })).toBeInTheDocument();
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

            renderSearchResultsPage();

            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
        });

        it('displays a message when a document search returns no results', async () => {
            mockedAxios.get.mockResolvedValue(async () => {
                return Promise.resolve({ data: [] });
            });

            renderSearchResultsPage();

            await waitFor(() => {
                expect(
                    screen.getByText('There are no documents available for this patient.'),
                ).toBeInTheDocument();
            });

            expect(
                screen.queryByRole('button', { name: 'Download All Documents' }),
            ).not.toBeInTheDocument();
            expect(
                screen.queryByRole('button', { name: 'Delete All Documents' }),
            ).not.toBeInTheDocument();
        });

        it('displays a error message when a document search fails', async () => {
            const errorResponse = {
                response: {
                    status: 400,
                    message: 'An error occurred',
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            renderSearchResultsPage();

            expect(await screen.findByRole('alert')).toBeInTheDocument();
            expect(
                screen.queryByRole('button', { name: 'Download All Documents' }),
            ).not.toBeInTheDocument();
            expect(
                screen.queryByRole('button', { name: 'Delete All Documents' }),
            ).not.toBeInTheDocument();
            expect(screen.getByRole('link', { name: 'Start Again' })).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('navigates to Start page when user clicks on start again button', async () => {
            const history = createMemoryHistory({
                initialEntries: ['/example'],
                initialIndex: 1,
            });

            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: [buildSearchResult()] }),
            );

            renderSearchResultsPage({}, history);

            expect(history.location.pathname).toBe('/example');

            await waitFor(() => {
                expect(screen.getByRole('link', { name: 'Start Again' })).toBeInTheDocument();
            });

            userEvent.click(screen.getByRole('link', { name: 'Start Again' }));

            await waitFor(() => {
                expect(history.location.pathname).toBe(routes.HOME);
            });
        });
    });
});

const homeRoute = '/example';
const renderSearchResultsPage = (
    patientOverride: Partial<PatientDetails> = {},
    history = createMemoryHistory({
        initialEntries: [homeRoute],
        initialIndex: 1,
    }),
) => {
    const patient: PatientDetails = {
        ...buildPatientDetails(),
        ...patientOverride,
    };

    render(
        <ReactRouter.Router navigator={history} location={homeRoute}>
            <PatientDetailsProvider patientDetails={patient}>
                <DocumentSearchResultsPage />
            </PatientDetailsProvider>
        </ReactRouter.Router>,
    );
};
