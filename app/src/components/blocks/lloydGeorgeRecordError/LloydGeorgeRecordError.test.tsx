import { act, render, screen } from '@testing-library/react';
import LloydGeorgeRecordError from './LloydGeorgeRecordError';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import { LinkProps } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';

const mockSetStage = jest.fn();
jest.mock('react-router-dom', () => ({
    __esModule: true,
    Link: (props: LinkProps) => <a {...props} role="link" />,
}));

describe('LloydGeorgeRecordError', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });
    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Rendering', () => {
        it("renders an error when the document download status is 'Timeout'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />,
            );

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i),
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
        });
        it("renders an error when the document download status is 'Failed'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.FAILED;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />,
            );

            expect(
                screen.getByText(/Sorry, the service is currently unavailable/i),
            ).toBeInTheDocument();
            expect(
                screen.getByText(/An error has occurred when creating the Lloyd George preview/i),
            ).toBeInTheDocument();
        });
        it("renders a message  when the document download status is 'No records'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.NO_RECORDS;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />,
            );

            expect(
                screen.getByText(/No documents are available for this patient/i),
            ).toBeInTheDocument();
        });
    });

    describe('Navigation', () => {
        it("renders a link that can navigate to the download all stage, when download status is 'Timeout'", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />,
            );

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i),
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
            expect(
                screen.getByRole('link', {
                    name: 'please download instead',
                }),
            ).toBeInTheDocument();
        });

        it("navigates to the download all stage, when download status is 'Timeout' and the link is clicked", () => {
            const timeoutStatus = DOWNLOAD_STAGE.TIMEOUT;
            render(
                <LloydGeorgeRecordError setStage={mockSetStage} downloadStage={timeoutStatus} />,
            );

            const downloadLink = screen.getByRole('link', {
                name: 'please download instead',
            });

            expect(
                screen.getByText(/The Lloyd George document is too large to view in a browser/i),
            ).toBeInTheDocument();
            expect(screen.getByText(/please download instead/i)).toBeInTheDocument();
            expect(downloadLink).toBeInTheDocument();

            act(() => {
                downloadLink.click();
            });

            expect(mockSetStage).toHaveBeenCalledWith(LG_RECORD_STAGE.DOWNLOAD_ALL);
        });
    });
});
