import { render, screen, waitFor } from '@testing-library/react';
import DocumentSearchResultsPage from './DocumentSearchResultsPage';
import userEvent from '@testing-library/user-event';
import { buildPatientDetails, buildSearchResult } from '../../helpers/test/testBuilders';
import { routes } from '../../types/generic/routes';
import axios from 'axios';
import usePatient from '../../helpers/hooks/usePatient';
import { LinkProps } from 'react-router-dom';

const mockedUseNavigate = jest.fn();
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => jest.fn(),
}));
jest.mock('../../helpers/hooks/useBaseAPIHeaders');
jest.mock('axios');
jest.mock('../../helpers/hooks/usePatient');

const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedUsePatient = usePatient as jest.Mock;
const mockPatient = buildPatientDetails();

describe('<DocumentSearchResultsPage />', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it('renders the page after a successful response from api', async () => {
            mockedAxios.get.mockResolvedValue(async () => {
                return Promise.resolve({ data: [buildSearchResult()] });
            });

            render(<DocumentSearchResultsPage />);

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

            render(<DocumentSearchResultsPage />);

            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
        });

        it('displays a message when a document search returns no results', async () => {
            mockedAxios.get.mockResolvedValue(async () => {
                return Promise.resolve({ data: [] });
            });

            render(<DocumentSearchResultsPage />);

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

            render(<DocumentSearchResultsPage />);

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
            mockedAxios.get.mockImplementation(() =>
                Promise.resolve({ data: [buildSearchResult()] }),
            );

            render(<DocumentSearchResultsPage />);

            await waitFor(() => {
                expect(screen.getByRole('link', { name: 'Start Again' })).toBeInTheDocument();
            });

            userEvent.click(screen.getByRole('link', { name: 'Start Again' }));

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.START);
            });
        });
    });
});
