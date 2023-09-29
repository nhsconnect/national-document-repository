import { Button } from 'nhsuk-react-components';
import SpinnerButton from '../../generic/spinnerButton/SpinnerButton';
import { routes } from '../../../types/generic/routes';
import { SUBMISSION_STATE } from '../../../types/pages/documentSearchResultsPage/types';
import { Link, useNavigate } from 'react-router-dom';
import getPresignedUrlForZip from '../../../helpers/requests/getPresignedUrlForZip';
import { AxiosError } from 'axios';
import { useBaseAPIUrl } from '../../../providers/configProvider/ConfigProvider';

type Props = {
    nhsNumber: string;
    downloadState: string;
    updateDownloadState: (newState: SUBMISSION_STATE) => void;
};

const DocumentSearchResultsOptions = (props: Props) => {
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();

    const downloadAll = async () => {
        props.updateDownloadState(SUBMISSION_STATE.PENDING);
        try {
            const preSignedUrl = await getPresignedUrlForZip({
                nhsNumber: props.nhsNumber,
                baseUrl: baseUrl,
            });

            downloadFile(preSignedUrl, `patient-record-${props.nhsNumber}`);

            props.updateDownloadState(SUBMISSION_STATE.SUCCEEDED);
        } catch (e) {
            const error = e as AxiosError;
            if (error.response?.status === 403) {
                navigate(routes.HOME);
            }
            props.updateDownloadState(SUBMISSION_STATE.FAILED);
        }
    };

    const downloadFile = (url: string, filename: string) => {
        const downloadLink = document.createElement('a');
        downloadLink.href = url;
        downloadLink.download = filename;

        downloadLink.click();
        downloadLink.remove();
    };

    return (
        <>
            <p>
                Only permanently delete all documents for this patient if you have a valid reason
                to. For example, if the retention period of these documents has been reached.
            </p>
            <div style={{ display: 'flex' }}>
                {props.downloadState === SUBMISSION_STATE.PENDING ? (
                    <SpinnerButton
                        data-testid="download-spinner"
                        status="Downloading documents"
                        disabled={true}
                    />
                ) : (
                    <Button type="button" onClick={downloadAll}>
                        Download All Documents
                    </Button>
                )}
                <Link
                    className="nhsuk-button nhsuk-button--secondary"
                    style={{ marginLeft: 72 }}
                    to={routes.DELETE_DOCUMENTS}
                    role="button"
                >
                    Delete All Documents
                </Link>
            </div>
            {props.downloadState === SUBMISSION_STATE.SUCCEEDED && (
                <p>
                    <strong>All documents have been successfully downloaded.</strong>
                </p>
            )}
        </>
    );
};

export default DocumentSearchResultsOptions;
