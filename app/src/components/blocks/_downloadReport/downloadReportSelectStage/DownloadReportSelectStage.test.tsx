import { render, screen, waitFor } from '@testing-library/react';
import { act } from 'react';
import DownloadReportSelectStage from './DownloadReportSelectStage';
import { getReportByType, REPORT_TYPE } from '../../../../types/generic/reports';
import { LinkProps } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { routes } from '../../../../types/generic/routes';
import downloadReport from '../../../../helpers/requests/downloadReport';
import { beforeEach, describe, expect, it, vi, MockedFunction } from 'vitest';

const mockDownloadReport = downloadReport as MockedFunction<typeof downloadReport>;

const mockedUseNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        Link: (props: LinkProps) => <a {...props} role="link" />,
        useNavigate: () => mockedUseNavigate,
    };
});
vi.mock('../../../../helpers/hooks/useBaseAPIUrl');
vi.mock('../../../../helpers/hooks/useBaseAPIHeaders');
vi.mock('../../../../helpers/requests/downloadReport');
vi.mock('../../../../helpers/utils/isLocal', () => ({
    isMock: () => false,
}));

describe('DownloadReportSelectStage', () => {
    beforeEach(() => {
        import.meta.env.VITE_ENVIRONMENT = 'vitest';
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

            const setDownloadError = vi.fn();
            vi.spyOn(React, 'useState').mockImplementation(() => ['', setDownloadError]);

            act(() => {
                render(<DownloadReportSelectStage report={report!} />);
            });
            await userEvent.click(
                screen.getByTestId(`download-${report?.fileTypes[0].extension}-button`),
            );
            waitFor(() => {
                expect(setDownloadError).toHaveBeenCalledTimes(1);
            });
        });

        it('should navigate to session expired when receiving a 403', async () => {
            const errorResponse = {
                response: {
                    status: 403,
                },
            };
            mockDownloadReport.mockImplementation(() => Promise.reject(errorResponse));

            const report = getReportByType(REPORT_TYPE.ODS_PATIENT_SUMMARY);

            const setDownloadError = vi.fn();
            vi.spyOn(React, 'useState').mockImplementation(() => ['', setDownloadError]);

            render(<DownloadReportSelectStage report={report!} />);

            await userEvent.click(
                screen.getByTestId(`download-${report?.fileTypes[0].extension}-button`),
            );
            await waitFor(() => {
                expect(mockedUseNavigate).toHaveBeenCalledWith(routes.SESSION_EXPIRED);
            });
        });
    });
});
