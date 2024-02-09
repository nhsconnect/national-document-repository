import { act, render, screen } from '@testing-library/react';
import LloydGeorgeRecordError from './LloydGeorgeRecordError';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import { LinkProps } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { routes } from '../../../types/generic/routes';
import useIsBSOL from '../../../helpers/hooks/useIsBSOL';

const mockSetStage = jest.fn();
const mockNavigate = jest.fn();
jest.mock('../../../helpers/hooks/useIsBSOL');

jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
    useNavigate: () => mockNavigate,
}));

jest.mock('react-router', () => ({
    useNavigate: () => mockNavigate,
}));

jest.mock('../../../helpers/hooks/useRole');
const mockUseRole = useRole as jest.Mock;
const mockedIsBSOL = useIsBSOL as jest.Mock;

describe('LloydGeorgeRecordError', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
        mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it("renders an error when the document download status is 'Timeout'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />
            );

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i)
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
        });
        it("renders an error when the document download status is 'Failed'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.FAILED;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />
            );

            expect(
                screen.getByText(/Sorry, the service is currently unavailable/i)
            ).toBeInTheDocument();
            expect(
                screen.getByText(/An error has occurred when creating the Lloyd George preview/i)
            ).toBeInTheDocument();
        });
        it("renders a message  when the document download status is 'No records' and user is non BSOL", () => {
            const timeoutStatus = DOWNLOAD_STAGE.NO_RECORDS;
            mockedIsBSOL.mockReturnValue(false);

            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />
            );

            expect(screen.getByText(/No documents are available/i)).toBeInTheDocument();
            expect(
                screen.queryByRole('button', { name: 'Upload patient record' })
            ).not.toBeInTheDocument();
        });
        it("renders a message and upload button when the document download status is 'No records' and user is admin BSOL", () => {
            const timeoutStatus = DOWNLOAD_STAGE.NO_RECORDS;
            mockedIsBSOL.mockReturnValue(true);
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_ADMIN);

            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />
            );

            expect(screen.getByText('No records available for this patient')).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: 'Upload patient record' })
            ).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it("renders a link that can navigate to the download all stage, when download status is 'Timeout'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />
            );

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i)
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
            expect(
                screen.getByRole('link', {
                    name: 'please download instead',
                })
            ).toBeInTheDocument();
        });

        it("navigates to the download all stage, when download status is 'Timeout' and the link is clicked: GP_ADMIN", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />
            );

            const downloadLink = screen.getByRole('link', {
                name: 'please download instead',
            });

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i)
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
            expect(downloadLink).toBeInTheDocument();

            act(() => {
                downloadLink.click();
            });

            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.DOWNLOAD_ALL);
        });

        it("navigates to unauthorised, when download status is 'Timeout' and the link is clicked: GP_CLINCIAL", () => {
            mockUseRole.mockReturnValue(REPOSITORY_ROLE.GP_CLINICAL);
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />
            );

            const downloadLink = screen.getByRole('link', {
                name: 'please download instead',
            });

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i)
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
            expect(downloadLink).toBeInTheDocument();

            act(() => {
                downloadLink.click();
            });

            expect(mockNavigate).toBeCalledWith(routes.UNAUTHORISED);
        });
    });
});
