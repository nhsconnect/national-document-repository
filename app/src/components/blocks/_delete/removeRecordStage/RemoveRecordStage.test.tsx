import { act, render, screen, waitFor } from '@testing-library/react';
import RemoveRecordStage from './RemoveRecordStage';
import usePatient from '../../../../helpers/hooks/usePatient';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import axios from 'axios';
import { routes } from '../../../../types/generic/routes';
import { MemoryHistory, createMemoryHistory } from 'history';
import * as ReactRouter from 'react-router-dom';
import waitForSeconds from '../../../../helpers/utils/waitForSeconds';
import { afterEach, beforeEach, describe, expect, it, vi, Mock, Mocked } from 'vitest';

vi.mock('axios');
vi.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});
vi.mock('react-router-dom', async () => ({
    ...(await vi.importActual('react-router-dom')),
    useNavigate: () => mockUseNavigate,
}));
vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('../../../../helpers/hooks/useRole');

const mockedAxios = axios as Mocked<typeof axios>;
const mockUseNavigate = vi.fn();
const mockUsePatient = usePatient as Mock;
const mockPatientDetails = buildPatientDetails();
const mockDownloadStage = vi.fn();
const mockResetDocState = vi.fn();

const testFileName1 = 'John_1';
const testFileName2 = 'John_2';
const numberOfFiles = 7;
const searchResults = [
    buildSearchResult({ fileName: testFileName1 }),
    buildSearchResult({ fileName: testFileName2 }),
];

let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('RemoveRecordStage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });
        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockUsePatient.mockReturnValue(mockPatientDetails);
    });
    afterEach(() => {
        vi.clearAllMocks();
    });
    describe('Render', () => {
        it('renders the component', () => {
            mockedAxios.get.mockImplementation(() => waitForSeconds(0));

            const recordType = 'Test Record';

            act(() => {
                renderComponent(history, numberOfFiles, recordType);
            });
            expect(
                screen.getByRole('heading', { name: 'Remove this ' + recordType + ' record' }),
            ).toBeInTheDocument();
            expect(
                screen.getByText(
                    /Only permanently remove this patient record if you have a valid reason to/i,
                ),
            ).toBeInTheDocument();
            expect(screen.getByRole('link', { name: 'Go back' })).toBeInTheDocument();
        });

        it('show progress bar when file search pending', () => {
            mockedAxios.get.mockImplementation(() => waitForSeconds(0));

            const recordType = 'Test Record';

            act(() => {
                renderComponent(history, numberOfFiles, recordType);
            });
            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
        });

        it('show service error when file search failed', async () => {
            const recordType = 'Test Record';
            const errorResponse = {
                response: {
                    status: 400,
                    data: { message: 'Error', err_code: 'SP_1001' },
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            act(() => {
                renderComponent(history, numberOfFiles, recordType);
            });
            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
            await waitFor(() => {
                expect(
                    screen.getByText(/Sorry, the service is currently unavailable/i),
                ).toBeInTheDocument();
            });

            expect(
                screen.queryByRole('button', { name: 'Remove all files' }),
            ).not.toBeInTheDocument();
        });

        it('show results when when file search succeeded', async () => {
            const recordType = 'Test Record';

            mockedAxios.get.mockImplementation(() => Promise.resolve({ data: searchResults }));

            act(() => {
                renderComponent(history, numberOfFiles, recordType);
            });
            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
            await waitFor(() => {
                expect(
                    screen.getByRole('button', { name: 'Remove all files' }),
                ).toBeInTheDocument();
            });

            expect(screen.getByText(searchResults[0].fileName)).toBeInTheDocument();
            expect(screen.getByText(searchResults[1].fileName)).toBeInTheDocument();
        });
    });

    describe('Navigate', () => {
        it('navigates to server error page when search 500', async () => {
            const recordType = 'Test Record';
            const errorResponse = {
                response: {
                    status: 500,
                    data: { message: 'Error', err_code: 'SP_1001' },
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            act(() => {
                renderComponent(history, numberOfFiles, recordType);
            });
            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
            const mockedShortcode = '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd';
            await waitFor(() => {
                expect(mockUseNavigate).toBeCalledWith(routes.SERVER_ERROR + mockedShortcode);
            });
        });

        it('navigates to session expired page when search 403', async () => {
            const recordType = 'Test Record';
            const errorResponse = {
                response: {
                    status: 403,
                    data: { message: 'Error', err_code: 'SP_1001' },
                },
            };
            mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));

            act(() => {
                renderComponent(history, numberOfFiles, recordType);
            });
            expect(screen.getByRole('progressbar', { name: 'Loading...' })).toBeInTheDocument();
            await waitFor(() => {
                expect(mockUseNavigate).toBeCalledWith(routes.SESSION_EXPIRED);
            });
        });
    });
});

const renderComponent = (history: MemoryHistory, numberOfFiles: number, recordType: string) => {
    return render(
        <ReactRouter.Router navigator={history} location={history.location}>
            <RemoveRecordStage
                numberOfFiles={numberOfFiles}
                recordType={recordType}
                setDownloadStage={mockDownloadStage}
                resetDocState={mockResetDocState}
            />
        </ReactRouter.Router>,
    );
};
