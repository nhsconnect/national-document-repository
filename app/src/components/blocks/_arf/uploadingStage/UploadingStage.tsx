import React from 'react';
import {
    UploadDocument,
    DOCUMENT_UPLOAD_STATE,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { Table, WarningCallout } from 'nhsuk-react-components';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import useTitle from '../../../../helpers/hooks/useTitle';

interface Props {
    documents: Array<UploadDocument>;
}

function UploadingStage({ documents }: Props) {
    const getUploadMessage = (type: DOCUMENT_UPLOAD_STATE) => {
        if (type === DOCUMENT_UPLOAD_STATE.SELECTED) return 'Waiting...';
        else if (type === DOCUMENT_UPLOAD_STATE.UPLOADING) return 'Uploading...';
        else if (type === DOCUMENT_UPLOAD_STATE.SUCCEEDED) return 'Uploaded';
        else if (type === DOCUMENT_UPLOAD_STATE.FAILED) return 'Upload failed';
        else if (type === DOCUMENT_UPLOAD_STATE.INFECTED) return 'File has failed a virus scan';
        else if (type === DOCUMENT_UPLOAD_STATE.SCANNING) return 'Virus scan in progress';
    };
    const pageHeader = 'Your documents are uploading';
    useTitle({ pageTitle: 'Uploading documents' });

    return (
        <>
            <h1 data-testid="arf-upload-uploading-stage-header">{pageHeader}</h1>
            <WarningCallout id="upload-stage-warning">
                <WarningCallout.Label>Stay on this page</WarningCallout.Label>
                <p>Do not close or navigate away from this browser until upload is complete.</p>
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
                        <Table.Cell>File Name</Table.Cell>
                        <Table.Cell>File Size</Table.Cell>
                        <Table.Cell>File Upload Progress</Table.Cell>
                    </Table.Row>
                </Table.Head>
                <Table.Body>
                    {documents.map((document) => (
                        <Table.Row key={document.id}>
                            <Table.Cell>{document.file.name}</Table.Cell>
                            <Table.Cell>{formatFileSize(document.file.size)}</Table.Cell>
                            <Table.Cell>
                                <progress
                                    aria-label={`Uploading ${document.file.name}`}
                                    max="100"
                                    value={document.progress}
                                ></progress>
                                <output aria-label={`${document.file.name} upload status`}>
                                    {document.state === DOCUMENT_UPLOAD_STATE.UPLOADING &&
                                    document.progress ? (
                                        <> {Math.round(document.progress)}% uploaded... </>
                                    ) : (
                                        <>{getUploadMessage(document.state)}</>
                                    )}
                                </output>
                            </Table.Cell>
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>
        </>
    );
}

export default UploadingStage;
