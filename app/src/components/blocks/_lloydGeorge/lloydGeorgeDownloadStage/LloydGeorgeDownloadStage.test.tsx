import { act, render, screen, waitFor } from '@testing-library/react';
import {
    buildConfig,
    buildLgSearchResult,
    buildPatientDetails,
} from '../../../../helpers/test/testBuilders';
import axios from 'axios';
import userEvent from '@testing-library/user-event';
import usePatient from '../../../../helpers/hooks/usePatient';
import { LinkProps } from 'react-router-dom';
import { routeChildren, routes } from '../../../../types/generic/routes';
import useConfig from '../../../../helpers/hooks/useConfig';
import { MemoryHistory, createMemoryHistory } from 'history';
import * as ReactRouter from 'react-router-dom';
import LloydGeorgeDownloadStage, { Props } from './LloydGeorgeDownloadStage';
import { runAxeTest } from '../../../../helpers/test/axeTestHelper';
import getPresignedUrlForZip from '../../../../helpers/requests/getPresignedUrlForZip';
import { DownloadManifestError } from '../../../../types/generic/errors';
import {
    afterEach,
    beforeEach,
    describe,
    expect,
    it,
    vi,
    Mock,
    Mocked,
    MockedFunction,
} from 'vitest';

const mockedUseNavigate = vi.fn();
const mockedAxios = axios as Mocked<typeof axios>;
const mockedUsePatient = usePatient as Mock;
const mockUseConfig = useConfig as Mock;
const mockPdf = buildLgSearchResult();
const mockPatient = buildPatientDetails();
const mockGetPresignedUrlForZip = getPresignedUrlForZip as MockedFunction<
    typeof getPresignedUrlForZip
>;

vi.mock('react-router-dom', async () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    ...(await vi.importActual('react-router-dom')),
    useNavigate: () => mockedUseNavigate,
}));
vi.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});
vi.mock('axios');
vi.mock('../../../../helpers/requests/getPresignedUrlForZip');
vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../../../helpers/hooks/usePatient');
vi.mock('../../../../helpers/hooks/useConfig');

let history = createMemoryHistory({
    initialEntries: ['/'],
    initialIndex: 0,
});

describe('LloydGeorgeDownloadStage', () => {
    beforeEach(() => {
        history = createMemoryHistory({
            initialEntries: ['/'],
            initialIndex: 0,
        });

        import.meta.env.VITE_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
        mockUseConfig.mockReturnValue(buildConfig());
    });
    afterEach(() => {
        vi.useRealTimers();
        vi.clearAllMocks();
    });

    it('renders the component', () => {
        renderComponent(history);

        expect(screen.getByRole('heading', { name: 'Downloading documents' })).toBeInTheDocument();
        expect(
            screen.getByRole('heading', {
                name: mockPatient.givenName + ' ' + mockPatient.familyName,
            }),
        ).toBeInTheDocument();
        expect(
            screen.getByRole('heading', {
                name: `NHS number: ${mockPatient.nhsNumber}`,
            }),
        ).toBeInTheDocument();

        const expectedTestId = 'download-file-header-' + mockPdf.numberOfFiles + '-files';
        expect(screen.getByTestId(expectedTestId)).toBeInTheDocument();
        expect(screen.getByTestId('cancel-download-link')).toHaveTextContent(
            'Cancel and return to patient record',
        );
    });

    it('renders a progress bar', () => {
        renderComponent(history);
        expect(screen.getByText('0% downloaded...')).toBeInTheDocument();
    });

    it('renders download complete on zip success', async () => {
        window.HTMLAnchorElement.prototype.click = vi.fn();
        mockGetPresignedUrlForZip.mockResolvedValue(mockPdf.presignedUrl);

        vi.useFakeTimers();

        renderComponent(history);

        expect(screen.getByText('0% downloaded...')).toBeInTheDocument();
        expect(screen.queryByText('100% downloaded...')).not.toBeInTheDocument();

        act(() => {
            vi.advanceTimersByTime(500);
        });

        await waitFor(() => {
            expect(screen.getByText('100% downloaded...')).toBeInTheDocument();
        });
        expect(screen.queryByText('0% downloaded...')).not.toBeInTheDocument();

        expect(screen.getByTestId(mockPdf.presignedUrl)).toBeInTheDocument();
        const urlLink = screen.getByTestId(mockPdf.presignedUrl);

        urlLink.addEventListener('click', (e) => {
            e.preventDefault();
        });
        act(() => {
            userEvent.click(urlLink);
        });

        await waitFor(async () => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(
                routeChildren.LLOYD_GEORGE_DOWNLOAD_COMPLETE,
            );
        });
    });

    it('pass accessibility checks', async () => {
        renderComponent(history);

        const results = await runAxeTest(document.body);
        expect(results).toHaveNoViolations();
    });

    it('navigates to Error page when zip lg record view return 500', async () => {
        const errorResponse = {
            response: {
                status: 500,
                data: { message: 'An error occurred', err_code: 'SP_1001' },
            },
        };
        mockGetPresignedUrlForZip.mockImplementation(() => Promise.reject(errorResponse));
        vi.useFakeTimers();
        renderComponent(history);
        act(() => {
            vi.advanceTimersByTime(500);
        });
        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(
                routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
            );
        });
    });

    it('navigates to Error page when GetPresignedUrlForZip throw DownloadManifestError', async () => {
        const mockError = new DownloadManifestError('some error msg');
        mockGetPresignedUrlForZip.mockImplementation(() => Promise.reject(mockError));
        vi.useFakeTimers();
        renderComponent(history);
        act(() => {
            vi.advanceTimersByTime(500);
        });
        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(
                expect.stringContaining(routes.SERVER_ERROR),
            );
        });
    });

    it('navigates to session expire page when zip lg record return 403', async () => {
        const errorResponse = {
            response: {
                status: 403,
                data: { message: 'Unauthorised' },
            },
        };
        mockGetPresignedUrlForZip.mockImplementation(() => Promise.reject(errorResponse));
        vi.useFakeTimers();
        renderComponent(history);
        act(() => {
            vi.advanceTimersByTime(500);
        });
        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
        });
    });
});

const renderComponent = (history: MemoryHistory, propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage' | 'setDownloadStage'> = {
        ...propsOverride,
        numberOfFiles: mockPdf.numberOfFiles,
    };

    return render(
        <ReactRouter.Router navigator={history} location={history.location}>
            <LloydGeorgeDownloadStage {...props} />
        </ReactRouter.Router>,
    );
};
