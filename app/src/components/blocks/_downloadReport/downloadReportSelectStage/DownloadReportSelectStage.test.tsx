import { render, screen, waitFor } from '@testing-library/react';
import DownloadReportSelectStage from './DownloadReportSelectStage';
import { getReportByType, REPORT_TYPE } from '../../../../types/generic/reports';
import { LinkProps } from 'react-router-dom';
import { act } from 'react-dom/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { routes } from '../../../../types/generic/routes';
import downloadReport from '../../../../helpers/requests/downloadReport';

const mockDownloadReport = downloadReport as jest.MockedFunction<typeof downloadReport>;

const mockedUseNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    Link: (props: LinkProps) => <a {...props} role="link" />,
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockedUseNavigate,
}));
jest.mock('../../../../helpers/hooks/useBaseAPIUrl');
jest.mock('../../../../helpers/hooks/useBaseAPIHeaders');
jest.mock('../../../../helpers/requests/downloadReport');
jest.mock('../../../../helpers/utils/isLocal', () => ({
    isMock: () => false,
}));

describe('DownloadReportSelectStage', () => {
    beforeEach(() => {
        process.env.REACT_APP_ENVIRONMENT = 'jest';
    });

    describe('Rendering', () => {
        it('should render the page correctly', async () => {
            const report = getReportByType(REPORT_TYPE.ODS_PATIENT_SUMMARY);
            render(<DownloadReportSelectStage report={report!} />);

            expect(screen.getByTestId('return-to-home-button')).toBeInTheDocument();
            const title = screen.getByTestId('title');
            expect(title).toBeInTheDocument();
            expect(title.innerHTML).toContain(report!.title);
            report!.fileTypes.forEach((fileType) => {
                expect(
                    screen.getByTestId(`download-${fileType.extension}-button`),
                ).toBeInTheDocument();
            });
            expect(screen.queryByTestId('error-notification-banner')).not.toBeInTheDocument();
        });

        it('should render error notification when download fails', async () => {
            const errorResponse = {
                response: {
                    status: 404,
                },
            };
            mockDownloadReport.mockImplementation(() => Promise.reject(errorResponse));

            const report = getReportByType(REPORT_TYPE.ODS_PATIENT_SUMMARY);

            const setDownloadError = jest.fn();
            jest.spyOn(React, 'useState').mockImplementation(() => ['', setDownloadError]);

            render(<DownloadReportSelectStage report={report!} />);

            userEvent.click(
                screen.getByTestId(`download-${report?.fileTypes[0].extension}-button`),
            );

            expect(setDownloadError).toHaveBeenCalledTimes(1);
        });

        it('should navigate to session expired when receiving a 403', async () => {
            const errorResponse = {
                response: {
                    status: 403,
                },
            };
            mockDownloadReport.mockImplementation(() => Promise.reject(errorResponse));

            const report = getReportByType(REPORT_TYPE.ODS_PATIENT_SUMMARY);

            const setDownloadError = jest.fn();
            jest.spyOn(React, 'useState').mockImplementation(() => ['', setDownloadError]);

            render(<DownloadReportSelectStage report={report!} />);

            act(() => {
                userEvent.click(
                    screen.getByTestId(`download-${report?.fileTypes[0].extension}-button`),
                );
            });

            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });
    });
});
