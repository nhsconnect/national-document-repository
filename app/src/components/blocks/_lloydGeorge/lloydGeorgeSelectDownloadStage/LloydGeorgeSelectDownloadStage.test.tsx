import { act, render, screen, waitFor } from '@testing-library/react';
import { buildPatientDetails, buildSearchResult } from '../../../../helpers/test/testBuilders';
import usePatient from '../../../../helpers/hooks/usePatient';
import LloydGeorgeSelectDownloadStage from './LloydGeorgeSelectDownloadStage';
import axios from 'axios';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { MemoryHistory, createMemoryHistory } from 'history';
import * as ReactRouter from 'react-router-dom';
import waitForSeconds from '../../../../helpers/utils/waitForSeconds';

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

describe('LloydGeorgeSelectDownloadStage', () => {
    beforeEach(() => {
        // temp solution to satisfy the pathname check within useEffect block
        // in the future, consider to replace window.location call with useLocation
        Object.defineProperty(window, 'location', {
            writable: true,
            value: {
                pathname: routeChildren.LLOYD_GEORGE_DOWNLOAD,
            },
        });

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

    it('renders the page header, patient details and loading text on page load', async () => {
        // suppress act() warning. postpone GET api response for 1 tick so that test complete before state change
        mockAxios.get.mockImplementationOnce(() => waitForSeconds(0));

        renderComponent(history);

        expect(
            screen.getByRole('heading', {
                name: 'Download the Lloyd George record for this patient',
            }),
        ).toBeInTheDocument();
        expect(screen.getByTestId('patient-summary')).toBeInTheDocument();
        expect(screen.getByText('Loading...')).toBeInTheDocument();
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
        expect(screen.getByTestId('toggle-selection-btn')).toBeInTheDocument();
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
