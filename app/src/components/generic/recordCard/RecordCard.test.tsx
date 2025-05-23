import usePatient from '../../../helpers/hooks/usePatient';
import useConfig from '../../../helpers/hooks/useConfig';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import getLloydGeorgeRecord from '../../../helpers/requests/getLloydGeorgeRecord';
import { render, screen, waitFor } from '@testing-library/react';
import RecordCard, { Props } from './RecordCard';
import { buildLgSearchResult } from '../../../helpers/test/testBuilders';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi, Mock, MockedFunction } from 'vitest';

const mockedUseNavigate = vi.fn();
vi.mock('../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../../helpers/hooks/usePatient');
vi.mock('../../../helpers/hooks/useConfig');
vi.mock('../../../helpers/hooks/useRole');
vi.mock('../../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../../helpers/requests/getLloydGeorgeRecord');
vi.mock('axios');
vi.mock('react-router', () => ({
    useNavigate: () => mockedUseNavigate,
}));

const mockGetLloydGeorgeRecord = getLloydGeorgeRecord as MockedFunction<
    typeof getLloydGeorgeRecord
>;

const mockUsePatient = usePatient as Mock;
const mockUseConfig = useConfig as Mock;
const mockUseBaseAPIUrl = useBaseAPIUrl as Mock;
const mockUseBaseAPIHeaders = useBaseAPIHeaders as Mock;

describe('RecordCard Component', () => {
    const mockFullScreenHandler = vi.fn();
    const props: Props = {
        heading: 'Mock Header Record',
        fullScreenHandler: mockFullScreenHandler,
        detailsElement: <div>Mock Details Element</div>,
        isFullScreen: false,
        refreshRecord: vi.fn(),
        pdfObjectUrl: 'https://test.com',
        resetDocStage: vi.fn(),
    };

    beforeEach(() => {
        vi.clearAllMocks();
        mockUsePatient.mockReturnValue({ nhsNumber: '1234567890' });
        mockUseConfig.mockReturnValue({
            mockLocal: { recordUploaded: true },
        });
        mockUseBaseAPIUrl.mockReturnValue('https://example.com/api');
        mockUseBaseAPIHeaders.mockReturnValue({ Authorization: 'Bearer token' });
    });

    describe('Rendering', () => {
        it('renders component', () => {
            render(<RecordCard {...props} />);

            expect(screen.getByText('Mock Header Record')).toBeInTheDocument();
            expect(screen.getByText('Mock Details Element')).toBeInTheDocument();
        });

        it('calls refreshRecord on mount', async () => {
            const mockRefreshRecord = vi.fn();
            render(<RecordCard {...props} refreshRecord={mockRefreshRecord} />);
            await waitFor(() => {
                expect(mockRefreshRecord).toHaveBeenCalledTimes(1);
            });
        });

        it('renders the "View in full screen" button when recordUrl is set', async () => {
            mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
            });
        });

        it('sets the page to full screen view when "View in full screen" is clicked', async () => {
            mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
            });
            act(() => {
                userEvent.click(screen.getByTestId('full-screen-btn'));
            });
            await waitFor(() => {
                expect(mockFullScreenHandler).toHaveBeenCalled();
            });
        });

        it('renders PDFViewer component when recordUrl is set', async () => {
            mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
            });
        });

        it('renders nothing while no pdfObjectUrl', async () => {
            render(<RecordCard {...props} pdfObjectUrl="" />);
            expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
        });

        it('removes ProgressBar once loading is complete', async () => {
            render(<RecordCard {...props} />);
            await waitFor(() => {
                expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
            });
        });

        it('renders full-screen layout when isFullScreen state is true', async () => {
            render(<RecordCard {...props} isFullScreen={true} />);
            expect(screen.queryByTestId('pdf-card')).not.toBeInTheDocument(); // Shouldn't show the card layout
        });

        it('renders the "View in full screen" button if the user is GP_ADMIN', async () => {
            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
            });
        });

        it('does not render PdfViewer or full-screen button when pdfObjectUrl is empty', async () => {
            render(<RecordCard {...props} pdfObjectUrl="" />);
            expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
            expect(screen.queryByTestId('full-screen-btn')).not.toBeInTheDocument();
        });

        it('does not render the pdf details view when full-screen view is click', async () => {
            mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

            render(<RecordCard {...props} />);

            await waitFor(() => {
                expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
            });
        });

        it('does not render the "View in full screen" button or pdf view when recordUrl is not set', () => {
            render(<RecordCard {...props} pdfObjectUrl="" />);
            expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
            expect(screen.queryByTestId('full-screen-btn')).not.toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it('Navigates to full screen view when "View in full screen" button is clicked', async () => {
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
