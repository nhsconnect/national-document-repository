import { Button } from 'nhsuk-react-components';
import SpinnerButton from '../../generic/spinnerButton/SpinnerButton';
import { routes } from '../../../types/generic/routes';
import { SUBMISSION_STATE } from '../../../types/pages/documentSearchResultsPage/types';
import { Link, useNavigate } from 'react-router-dom';
import getPresignedUrlForZip from '../../../helpers/requests/getPresignedUrlForZip';
import { AxiosError } from 'axios';
import { useBaseAPIUrl } from '../../../providers/configProvider/ConfigProvider';
import { useEffect, useRef, useState } from 'react';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';

type Props = {
    nhsNumber: string;
    downloadState: string;
    updateDownloadState: (newState: SUBMISSION_STATE) => void;
};

interface DownloadLinkAttributes {
    url: string;
    filename: string;
}

const DocumentSearchResultsOptions = (props: Props) => {
    const navigate = useNavigate();
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();
    const [linkAttributes, setLinkAttributes] = useState<DownloadLinkAttributes>({
        url: '',
        filename: '',
    });
    const linkRef = useRef<HTMLAnchorElement | null>(null);

    useEffect(() => {
        if (linkRef.current && linkAttributes.url) {
            linkRef.current.click();
        }
    }, [linkAttributes]);

    const downloadAll = async () => {
        props.updateDownloadState(SUBMISSION_STATE.PENDING);
        try {
            const preSignedUrl = await getPresignedUrlForZip({
                nhsNumber: props.nhsNumber,
                baseUrl: baseUrl,
                baseHeaders,
            });

            const filename = `patient-record-${props.nhsNumber}`;

            setLinkAttributes({ url: preSignedUrl, filename: filename });

            props.updateDownloadState(SUBMISSION_STATE.SUCCEEDED);
        } catch (e) {
            const error = e as AxiosError;
            if (error.response?.status === 403) {
                navigate(routes.HOME);
            }
            props.updateDownloadState(SUBMISSION_STATE.FAILED);
        }
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
                        id="download-spinner"
                        status="Downloading documents"
                        disabled={true}
                    />
                ) : (
                    <Button type="button" id="download-documents" onClick={downloadAll}>
                        Download All Documents
                    </Button>
                )}
                <a
                    hidden
                    id="download-link"
                    ref={linkRef}
                    href={linkAttributes.url}
                    download={linkAttributes.filename}
                >
                    Download Manifest URL
                </a>
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
