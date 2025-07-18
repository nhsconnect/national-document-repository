import { Table, WarningCallout } from 'nhsuk-react-components';
import useTitle from '../../../../helpers/hooks/useTitle';
import { getUploadMessage } from '../../../../helpers/utils/uploadAndScanDocumentHelpers';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { useNavigate } from 'react-router-dom';
import { routes } from '../../../../types/generic/routes';
import { useEffect } from 'react';

type Props = {
    documents: UploadDocument[];
};

const DocumentUploadingStage = ({ documents }: Props) => {
    const navigate = useNavigate();

    const pageHeader = 'Your documents are uploading';
    useTitle({ pageTitle: 'Uploading documents' });

    useEffect(() => {
        if (documents.length === 0) {
            navigate(routes.DOCUMENT_UPLOAD);
        }
    }, [navigate, documents]);

    return (
        <>
            <h1 data-testid="arf-upload-uploading-stage-header">{pageHeader}</h1>
            <WarningCallout id="upload-stage-warning">
                <WarningCallout.Label headingLevel="h2">Stay on this page</WarningCallout.Label>
                <p>
                    Do not close or navigate away from this page until upload is complete.{' '}
                    {documents.some((doc) => doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE) && (
                        <span>
                            Your Lloyd George files will be combined into one document when the
                            upload is complete.
                        </span>
                    )}
                </p>
            </WarningCallout>
            <Table
                responsive
                caption="Your documents are uploading"
                captionProps={{
                    className: 'nhsuk-u-visually-hidden',
                }}
            >
                <Table.Head>
                    <Table.Row>
                        <Table.Cell>Filename</Table.Cell>
                        <Table.Cell>Upload progress</Table.Cell>
                    </Table.Row>
                </Table.Head>
                <Table.Body>
                    {documents.map((document) => {
                        const isScanning = document.state === DOCUMENT_UPLOAD_STATE.SCANNING;
                        return (
                            <Table.Row key={document.id}>
                                <Table.Cell>{document.file.name}</Table.Cell>
                                <Table.Cell className="table-cell-uploading-cell-wide">
                                    <progress
                                        aria-label={`Uploading ${document.file.name}`}
                                        max="100"
                                        value={isScanning ? undefined : document.progress}
                                    ></progress>
                                    <br />
                                    <output aria-label={`${document.file.name} upload status`}>
                                        {getUploadMessage(document)}
                                    </output>
                                </Table.Cell>
                            </Table.Row>
                        );
                    })}
                </Table.Body>
            </Table>
        </>
    );
};

export default DocumentUploadingStage;
