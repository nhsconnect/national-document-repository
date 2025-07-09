import LloydGeorgeSummaryDescription from '../../components/blocks/_downloadReport/downloadReportSelectStage/ReportDescriptions/LloydGeorgeSummaryDescription';
import { endpoints } from './endpoints';

export enum REPORT_TYPE {
    ODS_PATIENT_SUMMARY = '0',
}

export type FileTypeData = {
    extension: string;
    label: string;
};

export type ReportData = {
    title: string;
    description: () => React.JSX.Element;
    fileTypes: FileTypeData[];
    reportType: REPORT_TYPE;
    endpoint: string;
};

export const getReportByType = (reportType: REPORT_TYPE): ReportData | undefined => {
    return reports.find((r) => r.reportType === reportType);
};

export const reports: ReportData[] = [
    {
        title: 'Lloyd George summary report',
        description: LloydGeorgeSummaryDescription,
        fileTypes: [
            { extension: 'csv', label: 'a CSV' },
            { extension: 'xlsx', label: 'an Excel' },
            { extension: 'pdf', label: 'a PDF' },
        ],
        reportType: REPORT_TYPE.ODS_PATIENT_SUMMARY,
        endpoint: endpoints.ODS_REPORT,
    },
];
