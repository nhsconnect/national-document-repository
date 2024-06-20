import React from 'react';

import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { Table, WarningCallout } from 'nhsuk-react-components';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import LinkButton from '../../../generic/linkButton/LinkButton';
import { UploadSession } from '../../../../types/generic/uploadResult';
import useTitle from '../../../../helpers/hooks/useTitle';

export type Props = {
    documents: Array<UploadDocument>;
    uploadSession: UploadSession | null;
    uploadAndScanDocuments: (
        documents: Array<UploadDocument>,
        uploadSession: UploadSession,
    ) => void;
};

function LloydGeorgeUploadStage({ documents, uploadSession, uploadAndScanDocuments }: Props) {
    const getUploadMessage = ({ state, progress }: UploadDocument) => {
        const showProgress = state === DOCUMENT_UPLOAD_STATE.UPLOADING && progress !== undefined;

        if (state === DOCUMENT_UPLOAD_STATE.SELECTED) return 'Waiting...';
        else if (showProgress) return `${Math.round(progress)}% uploaded...`;
        else if (state === DOCUMENT_UPLOAD_STATE.FAILED) return 'Upload failed';
        else if (state === DOCUMENT_UPLOAD_STATE.INFECTED) return 'File has failed a virus scan';
        else if (state === DOCUMENT_UPLOAD_STATE.CLEAN) return 'Virus scan complete';
        else if (state === DOCUMENT_UPLOAD_STATE.SCANNING) return 'Virus scan in progress';
        else if (state === DOCUMENT_UPLOAD_STATE.SUCCEEDED) return 'Upload succeeded';
        else {
            return 'Upload failed';
        }
    };
    const hasFailedUploads = documents.some(
        (d) =>
            !!d.attempts &&
            ![DOCUMENT_UPLOAD_STATE.UPLOADING, DOCUMENT_UPLOAD_STATE.SCANNING].includes(d.state),
    );

    const pageHeader = 'Uploading record';
    useTitle({ pageTitle: pageHeader });
    return (
        <>
            {hasFailedUploads && (
                <ErrorBox
                    errorBoxSummaryId="failed-uploads"
                    messageTitle="There is a problem with some of your files"
                    messageBody="Some of your files failed to upload, You cannot continue until you retry uploading these files."
                    messageLinkBody="Retry uploading all failed files"
                    dataTestId="retry-upload-error-box"
                    errorOnClick={() => {
                        const failedUploads = documents.filter((d) => {
                            const notInProgress = ![
                                DOCUMENT_UPLOAD_STATE.UPLOADING,
                                DOCUMENT_UPLOAD_STATE.SCANNING,
                            ].includes(d.state);
                            return d.attempts === 1 && notInProgress;
                        });
                        if (uploadSession) {
                            uploadAndScanDocuments(failedUploads, uploadSession);
                        }
                    }}
                />
            )}
            <h1>{pageHeader}</h1>
            <WarningCallout>
                <WarningCallout.Label headingLevel="h2">Stay on this page</WarningCallout.Label>
                <p>
                    Do not close or navigate away from this browser until upload is complete. Each
                    file will be uploaded and combined into one record.
                </p>
            </WarningCallout>
            <Table
                responsive
                caption="Your documents are uploading"
                captionProps={{
                    className: 'nhsuk-u-visually-hidden',
                }}
                data-testid="upload-documents-table"
            >
                <Table.Head>
                    <Table.Row>
                        <Table.Cell>Filename</Table.Cell>
                        <Table.Cell style={{ width: '140px' }}>Size</Table.Cell>
                        <Table.Cell style={{ width: '200px' }}>Upload progress</Table.Cell>
                    </Table.Row>
                </Table.Head>
                <Table.Body>
                    {documents.map((document) => {
                        const notInProgress = ![
                            DOCUMENT_UPLOAD_STATE.UPLOADING,
                            DOCUMENT_UPLOAD_STATE.SCANNING,
                        ].includes(document.state);

                        const uploadFailed = !!document.attempts && notInProgress;

                        return (
                            <Table.Row key={document.id}>
                                <Table.Cell>
                                    <div>{document.file.name}</div>
                                    {uploadFailed && (
                                        <strong className="nhs-warning-color">
                                            File failed to upload
                                        </strong>
                                    )}
                                </Table.Cell>
                                <Table.Cell style={{ width: '140px' }}>
                                    {formatFileSize(document.file.size)}
                                </Table.Cell>
                                <Table.Cell style={{ width: '200px' }}>
                                    <progress
                                        aria-label={`Uploading ${document.file.name}`}
                                        max="100"
                                        value={document.progress}
                                    ></progress>
                                    <output aria-label={`${document.file.name} upload status`}>
                                        {getUploadMessage(document)}
                                    </output>
                                    {uploadFailed && (
                                        <div style={{ textAlign: 'right' }}>
                                            <LinkButton
                                                onClick={() => {
                                                    if (uploadSession) {
                                                        uploadAndScanDocuments(
                                                            [document],
                                                            uploadSession,
                                                        );
                                                    }
                                                }}
                                            >
                                                Retry upload
                                            </LinkButton>
                                        </div>
                                    )}
                                </Table.Cell>
                            </Table.Row>
                        );
                    })}
                </Table.Body>
            </Table>
        </>
    );
}

export default LloydGeorgeUploadStage;
