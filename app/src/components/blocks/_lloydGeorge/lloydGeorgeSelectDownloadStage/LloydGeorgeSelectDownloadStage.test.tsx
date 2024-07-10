import { act, render, screen, waitFor } from '@testing-library/react';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import LloydGeorgeSelectDownloadStage from './LloydGeorgeSelectDownloadStage';
import axios from 'axios';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { MemoryHistory, createMemoryHistory } from 'history';
import * as ReactRouter from 'react-router-dom';

const mockAxios = axios as jest.Mocked<typeof axios>;
const mockPatient = buildPatientDetails();
const mockedUsePatient = usePatient as jest.Mock;
const mockNavigate = jest.fn();
const mockSetDownloadStage = jest.fn();

jest.mock('../../../../helpers/hooks/usePatient');
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('axios');

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
}));
jest.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});

let history: MemoryHistory = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

const searchResults = [
    buildSearchResult({ fileName: '1of2_test.pdf', ID: 'test-id-1' }),
    buildSearchResult({ fileName: '2of2_test.pdf', ID: 'test-id-2' }),
    buildSearchResult({ fileName: '1of1_test.pdf', ID: 'test-id-3' }),
];

// This page has a specific url check to trigger a api call when on the select file view
global.window = Object.create(window);
Object.defineProperty(window, 'location', {
    value: {
        pathname: routeChildren.LLOYD_GEORGE_DOWNLOAD,
    },
    writable: true, // possibility to override
});

describe('LloydGeorgeSelectDownloadStage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });

        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the page header, patient details and loading text on page load', () => {
        renderComponent(history);

        expect(
            screen.getByRole('heading', {
                name: 'Download the Lloyd George record for this patient',
            }),
        ).toBeInTheDocument();
        expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        expect(screen.getByText('Loading...')).toBeInTheDocument();
        expect(screen.queryByTestId('available-files-table-title')).not.toBeInTheDocument();
    });

    it('renders list of files in record when axios get request is successful', async () => {
        mockAxios.get.mockReturnValue(Promise.resolve({ data: searchResults }));

        act(() => {
            renderComponent(history);
        });

        await waitFor(async () => {
            expect(screen.getByTestId('available-files-table-title')).toBeInTheDocument();
        });
        expect(screen.getByTestId('search-result-0')).toBeInTheDocument();
        expect(screen.getByTestId('download-selected-files-btn')).toBeInTheDocument();
        expect(screen.getByTestId('download-all-files-btn')).toBeInTheDocument();
        expect(screen.getByTestId('start-again-link')).toBeInTheDocument();
    });

    it('navigates to session expired page when get request returns 403', async () => {
        const errorResponse = {
            response: {
                status: 403,
                data: { message: 'Unauthorised' },
            },
        };
        mockAxios.get.mockImplementation(() => Promise.reject(errorResponse));

        act(() => {
            renderComponent(history);
        });

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
        });
    });

    it('navigates to server error page when get request returns 5XX', async () => {
        const errorResponse = {
            response: {
                status: 500,
                data: { message: 'Server error', err_code: 'SP_1001' },
            },
        };
        mockAxios.get.mockImplementation(() => Promise.reject(errorResponse));

        act(() => {
            renderComponent(history);
        });

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith(
                routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
            );
        });
    });
});

const renderComponent = (history: MemoryHistory, deleteAfterDownload = false) => {
    return render(
        <ReactRouter.Router navigator={history} location={history.location}>
            <LloydGeorgeSelectDownloadStage
                setDownloadStage={mockSetDownloadStage}
                numberOfFiles={2}
                deleteAfterDownload={deleteAfterDownload}
            />
        </ReactRouter.Router>,
    );
};
