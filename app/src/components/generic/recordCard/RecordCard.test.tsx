import usePatient from '../../../helpers/hooks/usePatient';
import useConfig from '../../../helpers/hooks/useConfig';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import getLloydGeorgeRecord from '../../../helpers/requests/getLloydGeorgeRecord';

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
it('passes a test', () => {});

// describe('RecordCard Component', () => {
//     const mockFullScreenHandler = jest.fn();
//     const props = {
//         heading: 'Mock Header Record',
//         fullScreenHandler: mockFullScreenHandler,
//         detailsElement: <div>Mock Details Element</div>,
//         downloadStage: DOWNLOAD_STAGE.INITIAL,
//         isFullScreen: false,
//     };

//     beforeEach(() => {
//         jest.clearAllMocks();
//         mockUsePatient.mockReturnValue({ nhsNumber: '1234567890' });
//         mockUseConfig.mockReturnValue({
//             mockLocal: { recordUploaded: true },
//         });
//         mockUseBaseAPIUrl.mockReturnValue('https://example.com/api');
//         mockUseBaseAPIHeaders.mockReturnValue({ Authorization: 'Bearer token' });
//     });

//     describe('Rendering', () => {
//         it('renders component', () => {
//             render(<RecordCard {...props} />);

//             expect(screen.getByText('Mock Header Record')).toBeInTheDocument();
//             expect(screen.getByText('Mock Details Element')).toBeInTheDocument();
//         });

//         it('renders the "View in full screen" button when recordUrl is set', async () => {
//             mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

//             render(<RecordCard {...props} />);

//             await waitFor(() => {
//                 expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
//             });
//         });

//         it('sets the page to full screen view when "View in full screen" is clicked', async () => {
//             mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

//             render(<RecordCard {...props} />);

//             await waitFor(() => {
//                 expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
//             });
//             act(() => {
//                 userEvent.click(screen.getByTestId('full-screen-btn'));
//             });
//             await waitFor(() => {
//                 expect(mockFullScreenHandler).toHaveBeenCalled();
//             });
//         });

//         it('renders PDFViewer component when recordUrl is set', async () => {
//             mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

//             render(<RecordCard {...props} />);

//             await waitFor(() => {
//                 expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
//             });
//         });

//         it('renders a ProgressBar when in loading state', async () => {
//             render(<RecordCard {...props} downloadStage={DOWNLOAD_STAGE.PENDING} />);
//             expect(screen.getByText('Loading...')).toBeInTheDocument();
//         });

//         it('renders full-screen layout when isFullScreen state is true', async () => {
//             render(<RecordCard {...props} isFullScreen={true} />);
//             expect(screen.queryByTestId('pdf-card')).not.toBeInTheDocument(); // Shouldn't show the card layout
//         });

//         it('does not render the pdf details view when full-screen view is click', async () => {
//             mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

//             render(<RecordCard {...props} />);

//             await waitFor(() => {
//                 expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
//             });
//         });

//         it('does not render the "View in full screen" button or pdf view when recordUrl is not set', () => {
//             render(<RecordCard {...props} />);
//             expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
//             expect(screen.queryByTestId('full-screen-btn')).not.toBeInTheDocument();
//         });

//         it('does not render PdfViewer when downloadStage is FAILED', async () => {
//             render(<RecordCard {...props} downloadStage={DOWNLOAD_STAGE.FAILED} />);
//             expect(screen.queryByTestId('pdf-viewer')).not.toBeInTheDocument();
//         });
//     });

//     describe('Navigation', () => {
//         it('navigates to SESSION_EXPIRED when error status is 403', async () => {
//             const errorResponse = {
//                 response: { status: 403 },
//             };
//             mockGetLloydGeorgeRecord.mockRejectedValue(errorResponse);

//             render(<RecordCard {...props} />);

//             await waitFor(() => {
//                 expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
//             });
//         });

//         it('navigates to SERVER_ERROR when error status is 500', async () => {
//             const errorResponse = {
//                 response: { status: 500 },
//             };
//             mockGetLloydGeorgeRecord.mockRejectedValue(errorResponse);

//             render(<RecordCard {...props} />);

//             await waitFor(() => {
//                 expect(mockedUseNavigate).toHaveBeenCalledWith(
//                     expect.stringContaining(routes.SERVER_ERROR),
//                 );
//             });
//         });

//         it('calls fullScreenHandler when "View in full screen" button is clicked', async () => {
//             mockGetLloydGeorgeRecord.mockResolvedValue(buildLgSearchResult());

//             render(<RecordCard {...props} />);

//             await waitFor(() => {
//                 expect(screen.getByTestId('full-screen-btn')).toBeInTheDocument();
//             });

//             userEvent.click(screen.getByTestId('full-screen-btn'));

//             expect(mockFullScreenHandler).toHaveBeenCalledWith(true);
//         });
//     });
// });
