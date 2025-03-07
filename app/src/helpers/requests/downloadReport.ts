import { AuthHeaders } from '../../types/blocks/authHeaders';
import axios, { AxiosError } from 'axios';
import { ReportData } from '../../types/generic/reports';

type Args = {
    report: ReportData;
    fileType: string;
    baseUrl: string;
    baseHeaders: AuthHeaders;
};

type DownloadReportResponseData = {
    data: { url: string };
};

const downloadReport = async ({ report, fileType, baseUrl, baseHeaders }: Args): Promise<void> => {
    const gatewayUrl = baseUrl + report.endpoint;

    try {
        const { data }: DownloadReportResponseData = await axios.get(gatewayUrl, {
            headers: {
                ...baseHeaders,
            },
            params: {
                outputFileFormat: fileType,
            },
        });

        const link = document.createElement('a');
        link.href = data.url;
        link.setAttribute('download', '');

        link.click();
    } catch (e) {
        const error = e as AxiosError;
        throw error;
    }
};

export default downloadReport;
