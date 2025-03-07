import { render, screen } from '@testing-library/react';
import DownloadReportCompleteStage from "./DownloadReportCompleteStage";
import { REPORT_TYPE, ReportData } from "../../../../types/generic/reports";
import { getFormattedDate } from '../../../../helpers/utils/formatDate';

describe('DownloadReportCompleteStage', () => {
    it('should render correctly', () => {
        const report = {
            title: 'title',
            reportType: REPORT_TYPE.ODS_PATIENT_SUMMARY
        } as ReportData;

        render(<DownloadReportCompleteStage report={report}/>);

        const title = screen.getByTestId('report-download-complete-header');
        expect(title).toBeInTheDocument();
        expect(title.innerHTML).toContain(report.title);

        const downloadDate = screen.getByTestId('report-download-complete-date');
        expect(downloadDate).toBeInTheDocument();
        expect(downloadDate.innerHTML).toBe(getFormattedDate(new Date()));

        expect(screen.getByTestId('home-button')).toBeInTheDocument();
        expect(screen.getByTestId('back-to-download-page-button')).toBeInTheDocument();
    });
});