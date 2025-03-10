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
import { getUploadMessage } from '../../../../helpers/utils/uploadAndScanDocumentHelpers';

export type Props = {
    documents: Array<UploadDocument>;
    uploadSession: UploadSession | null;
    uploadAndScanDocuments: (
        documents: Array<UploadDocument>,
        uploadSession: UploadSession,
        nhsNumber: string,
    ) => void;
    nhsNumber: string;
};

function LloydGeorgeUploadStage({
    documents,
    uploadSession,
    uploadAndScanDocuments,
    nhsNumber,
}: Props) {
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
                            uploadAndScanDocuments(failedUploads, uploadSession, nhsNumber);
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
                        <Table.Cell className="lg-upload-thin-table-cell">Size</Table.Cell>
                        <Table.Cell className="lg-upload-thick-table-cell">
                            Upload progress
                        </Table.Cell>
                    </Table.Row>
                </Table.Head>
                <Table.Body>
                    {documents.map((document) => {
                        const notInProgress = ![
                            DOCUMENT_UPLOAD_STATE.UPLOADING,
                            DOCUMENT_UPLOAD_STATE.SCANNING,
                        ].includes(document.state);
                        const isScanning = document.state === DOCUMENT_UPLOAD_STATE.SCANNING;

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
                                <Table.Cell className="lg-upload-thin-table-cell">
                                    {formatFileSize(document.file.size)}
                                </Table.Cell>
                                <Table.Cell className="lg-upload-thick-table-cell">
                                    <progress
                                        aria-label={`Uploading ${document.file.name}`}
                                        max="100"
                                        value={isScanning ? undefined : document.progress}
                                    ></progress>
                                    <output aria-label={`${document.file.name} upload status`}>
                                        {getUploadMessage(document)}
                                    </output>
                                    {uploadFailed && (
                                        <div className="lg-upload-failed-div">
                                            <LinkButton
                                                onClick={() => {
                                                    if (uploadSession) {
                                                        uploadAndScanDocuments(
                                                            [document],
                                                            uploadSession,
                                                            nhsNumber,
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
