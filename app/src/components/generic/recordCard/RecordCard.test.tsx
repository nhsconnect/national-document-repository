import { render, screen, waitFor } from '@testing-library/react';
import RecordCard from './RecordCard';
import userEvent from '@testing-library/user-event';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import { routes } from '../../../types/generic/routes';
import usePatient from '../../../helpers/hooks/usePatient';
import useConfig from '../../../helpers/hooks/useConfig';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import getLloydGeorgeRecord from '../../../helpers/requests/getLloydGeorgeRecord';
import { buildLgSearchResult } from '../../../helpers/test/testBuilders';

const mockedUseNavigate = jest.fn();
jest.mock('../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../helpers/hooks/usePatient');
jest.mock('../../../helpers/hooks/useConfig');
jest.mock('../../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../../helpers/requests/getLloydGeorgeRecord');
jest.mock('axios');
jest.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));

const mockGetLloydGeorgeRecord = getLloydGeorgeRecord as jest.MockedFunction<
    typeof getLloydGeorgeRecord
>;

const mockUsePatient = usePatient as jest.Mock;
const mockUseConfig = useConfig as jest.Mock;
const mockUseBaseAPIUrl = useBaseAPIUrl as jest.Mock;
const mockUseBaseAPIHeaders = useBaseAPIHeaders as jest.Mock;

describe('RecordCard Component', () => {
    const mockFullScreenHandler = jest.fn();
    const props = {
        heading: 'Test Record',
        fullScreenHandler: mockFullScreenHandler,
        detailsElement: <div>Details Element</div>,
        downloadStage: DOWNLOAD_STAGE.INITIAL,
        isFullScreen: false,
    };

    beforeEach(() => {
        jest.clearAllMocks();
        mockUsePatient.mockReturnValue({ nhsNumber: '1234567890' });
        mockUseConfig.mockReturnValue({
            mockLocal: { recordUploaded: true },
        });
        mockUseBaseAPIUrl.mockReturnValue('https://example.com/api');
        mockUseBaseAPIHeaders.mockReturnValue({ Authorization: 'Bearer token' });
    });

    describe('Rendering', () => {
        it('renders the heading and detailsElement', () => {
            render(<RecordCard {...props} />);

            expect(screen.getByText('Test Record')).toBeInTheDocument();
            expect(screen.getByText('Details Element')).toBeInTheDocument();
        });

        it('renders the "View in full screen" button when recordUrl is set', async () => {
            mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
            });
        });

        it('does not render the "View in full screen" button when recordUrl is not set', () => {
            render(<RecordCard {...props} />);

            expect(screen.queryByTestId('full-screen-btn')).not.toBeInTheDocument();
        });

        it('renders PDFViewer component when recordUrl is present', async () => {
            mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
            });
        });
    });

    describe('Navigation', () => {
        it('navigates to SESSION_EXPIRED when error status is 403', async () => {
            const errorResponse = {
                response: { status: 403 },
            };
            mockGetLloydGeorgeRecord.mockRejectedValue(errorResponse);

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });

        it('navigates to SERVER_ERROR when error status is 500', async () => {
            const errorResponse = {
                response: { status: 500 },
            };
            mockGetLloydGeorgeRecord.mockRejectedValue(errorResponse);

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(
                    expect.stringContaining(routes.SERVER_ERROR),
                );
            });
        });

        it('calls fullScreenHandler when "View in full screen" button is clicked', async () => {
            mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
            });

            userEvent.click(screen.getByTestId('full-screen-btn'));

            expect(mockFullScreenHandler).toHaveBeenCalledWith(true);
        });
    });
});
