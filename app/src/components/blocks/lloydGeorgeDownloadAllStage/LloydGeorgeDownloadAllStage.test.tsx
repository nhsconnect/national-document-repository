import { render, screen, waitFor } from '@testing-library/react';
import LgDownloadAllStage, { Props } from './LloydGeorgeDownloadAllStage';
import {
    buildConfig,
    buildLgSearchResult,
    buildPatientDetails,
} from '../../../helpers/test/testBuilders';
import axios from 'axios';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import usePatient from '../../../helpers/hooks/usePatient';
import { LinkProps } from 'react-router-dom';
import { routes } from '../../../types/generic/routes';
import useConfig from '../../../helpers/hooks/useConfig';

const mockedUseNavigate = jest.fn();
const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedUsePatient = usePatient as jest.Mock;
const mockUseConfig = useConfig as jest.Mock;
const mockPdf = buildLgSearchResult();
const mockPatient = buildPatientDetails();
const mockSetStage = jest.fn();
const mockDownloadStage = jest.fn();
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('moment', () => {
    return () => jest.requireActual('moment')('2020-01-01T00:00:00.000Z');
});
jest.mock('axios');
jest.mock('../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../helpers/hooks/usePatient');
jest.mock('../../../helpers/hooks/useConfig');

describe('LloydGeorgeDownloadAllStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockedUsePatient.mockReturnValue(mockPatient);
        mockUseConfig.mockReturnValue(buildConfig());
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    it('renders the component', () => {
        renderComponent();

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
        expect(
            screen.getByRole('heading', {
                name: `Preparing download for ${mockPdf.number_of_files} files`,
            }),
        ).toBeInTheDocument();
    });

    it('renders a progress bar', () => {
        renderComponent();
        expect(screen.getByText('0% downloaded...')).toBeInTheDocument();
    });

    it('renders download complete on zip success', async () => {
        window.HTMLAnchorElement.prototype.click = jest.fn();
        mockedAxios.get.mockImplementation(() => Promise.resolve({ data: mockPdf.presign_url }));

        jest.useFakeTimers();

        renderComponent();

        expect(screen.getByText('0% downloaded...')).toBeInTheDocument();
        expect(screen.queryByText('100% downloaded...')).not.toBeInTheDocument();

        act(() => {
            jest.advanceTimersByTime(500);
        });

        await waitFor(() => {
            expect(screen.getByText('100% downloaded...')).toBeInTheDocument();
        });
        expect(screen.queryByText('0% downloaded...')).not.toBeInTheDocument();

        expect(screen.getByTestId(mockPdf.presign_url)).toBeInTheDocument();
        const urlLink = screen.getByTestId(mockPdf.presign_url);

        urlLink.addEventListener('click', (e) => {
            e.preventDefault();
        });
        act(() => {
            userEvent.click(urlLink);
        });

        await waitFor(async () => {
            expect(screen.queryByText('Downloading documents')).not.toBeInTheDocument();
        });
        expect(screen.getByRole('heading', { name: 'Download complete' })).toBeInTheDocument();
    });

    it('navigates to Error page when zip lg record view complete but fail on delete', async () => {
        window.HTMLAnchorElement.prototype.click = jest.fn();
        mockedAxios.get.mockImplementation(() => Promise.resolve({ data: mockPdf.presign_url }));
        const errorResponse = {
            response: {
                status: 500,
                data: { message: 'An error occurred', err_code: 'SP_1001' },
            },
        };
        mockedAxios.delete.mockImplementation(() => Promise.reject(errorResponse));

        jest.useFakeTimers();

        renderComponent({ deleteAfterDownload: true });

        expect(screen.getByText('0% downloaded...')).toBeInTheDocument();
        expect(screen.queryByText('100% downloaded...')).not.toBeInTheDocument();

        act(() => {
            jest.advanceTimersByTime(500);
        });

        await waitFor(() => {
            expect(screen.getByText('100% downloaded...')).toBeInTheDocument();
        });
        expect(screen.queryByText('0% downloaded...')).not.toBeInTheDocument();

        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(
                routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
            );
        });
    });

    it('navigates to Error page when zip lg record view return 500', async () => {
        const errorResponse = {
            response: {
                status: 500,
                data: { message: 'An error occurred', err_code: 'SP_1001' },
            },
        };
        mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));
        jest.useFakeTimers();
        renderComponent();
        act(() => {
            jest.advanceTimersByTime(500);
        });
        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(
                routes.SERVER_ERROR + '?encodedError=WyJTUF8xMDAxIiwiMTU3NzgzNjgwMCJd',
            );
        });
    });

    it('navigates to session expire page when zip lg record view return 403', async () => {
        const errorResponse = {
            response: {
                status: 403,
                data: { message: 'Unauthorised' },
            },
        };
        mockedAxios.get.mockImplementation(() => Promise.reject(errorResponse));
        jest.useFakeTimers();
        renderComponent();
        act(() => {
            jest.advanceTimersByTime(500);
        });
        await waitFor(() => {
            expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
        });
    });
});

const renderComponent = (propsOverride?: Partial<Props>) => {
    const props: Omit<Props, 'setStage' | 'setDownloadStage'> = {
        numberOfFiles: mockPdf.number_of_files,
        deleteAfterDownload: false,
        ...propsOverride,
    };

    return render(
        <LgDownloadAllStage
            {...props}
            setStage={mockSetStage}
            setDownloadStage={mockDownloadStage}
        />,
    );
};
