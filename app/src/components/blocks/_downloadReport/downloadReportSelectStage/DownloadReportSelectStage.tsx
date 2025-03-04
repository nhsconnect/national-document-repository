import { useNavigate } from 'react-router-dom';
import { FileTypeData, ReportData } from '../../../../types/generic/reports';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { BackLink, Button } from 'nhsuk-react-components';
import downloadReport from '../../../../helpers/requests/downloadReport';
import useBaseAPIUrl from '../../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../../helpers/hooks/useBaseAPIHeaders';
import { AxiosError } from 'axios';
import { isMock } from '../../../../helpers/utils/isLocal';
import { ReactNode, useRef, useState } from 'react';
import NotificationBanner from '../../../layout/notificationBanner/NotificationBanner';
import SpinnerButton from '../../../generic/spinnerButton/SpinnerButton';

type Props = {
    report: ReportData;
};

const DownloadReportSelectStage = (props: Props) => {
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const navigate = useNavigate();
    const [downloading, setDownloading] = useState(false);
    const [downloadError, setDownloadError] = useState<ReactNode>(null);
    const scrollToRef = useRef<HTMLDivElement>(null);

    const handleSuccess = () => {
        navigate(`${routeChildren.REPORT_DOWNLOAD_COMPLETE}?reportType=${props.report.reportType}`);
    };

    const noDataContent = () => {
        return (
            <>
                <h3>Report could not be created</h3>
                <p>
                    There are currently no records stored in this service for your
                    organisation.&nbsp; See our&nbsp;
                    <a
                        href="https://digital.nhs.uk/services/access-and-store-digital-patient-documents/help-and-guidance/problems-with-signing-in"
                        title="https://digital.nhs.uk/services/access-and-store-digital-patient-documents/help-and-guidance/problems-with-signing-in"
                        target="_blank"
                        rel="noreferrer"
                        aria-label="Help and guidance - this link will open in a new tab"
                    >
                        Help and guidance
                    </a>
                    &nbsp;pages for more information.
                </p>
            </>
        );
    };

    const serverErrorContent = () => {
        return (
            <>
                <h3>Download failed</h3>
                <p>
                    The selected report could not be downloaded. Wait a few minutes and try&nbsp;
                    again. If this problem continues, contact the National Service Desk&nbsp; (NSD)
                    by calling 0300 303 5035 or by emailing&nbsp;
                    <a
                        href="mailto:ssd.nationalservicedesk@nhs.net"
                        title="email ssd.nationalservicedesk@nhs.net"
                    >
                        ssd.nationalservicedesk@nhs.net
                    </a>
                    .
                </p>
            </>
        );
    };

    const handleError = (errorCode: number) => {
        const error = errorCode === 404 ? noDataContent() : serverErrorContent();
        setDownloadError(error);
        scrollToRef.current?.scrollIntoView();
    };

    const handleDownload = async (fileType: string) => {
        setDownloading(true);

        try {
            await downloadReport({ report: props.report, fileType, baseUrl, baseHeaders });
            handleSuccess();
        } catch (e) {
            const error = e as AxiosError;
            /* istanbul ignore if */
            if (isMock(error)) {
                handleSuccess();
            } else {
                handleError(error.response!.status);
            }
        }

        setDownloading(false);
    };

    const DownloadLinks = (fileTypes: FileTypeData[]) => {
        if (downloading) {
            return (
                <SpinnerButton id="download-spinner" status="Downloading report" disabled={true} />
            );
        }

        return fileTypes.map((fileType) => {
            return (
                <Button
                    data-testid={`download-${fileType.extension}-button`}
                    secondary
                    className="mb-5"
                    onClick={async () => {
                        handleDownload(fileType.extension);
                    }}
                    key={fileType.extension}
                >
                    Download as {fileType.label} file
                </Button>
            );
        });
    };

    return (
        <>
            <BackLink
                data-testid="return-to-home-button"
                asElement="a"
                href={routes.HOME}
                className="mb-5"
            >
                Return to Home
            </BackLink>
            {downloadError && (
                <NotificationBanner
                    title="Important"
                    className="download-failed-banner"
                    scrollToRef={scrollToRef}
                    dataTestId="error-notification-banner"
                >
                    {downloadError}
                </NotificationBanner>
            )}
            <h1 data-testid="title">Download the {props.report?.title}</h1>
            <div className="mb-7">{<props.report.description />}</div>
            <h2>Choose a file format:</h2>

            <div className="button-list">{DownloadLinks(props.report.fileTypes)}</div>
        </>
    );
};

export default DownloadReportSelectStage;
