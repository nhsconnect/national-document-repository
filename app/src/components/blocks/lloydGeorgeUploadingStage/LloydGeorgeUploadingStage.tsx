import React, { Dispatch, SetStateAction, useEffect } from 'react';
import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import { Table, WarningCallout } from 'nhsuk-react-components';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import ErrorBox from '../../layout/errorBox/ErrorBox';
import LinkButton from '../../generic/linkButton/LinkButton';
import usePatient from '../../../helpers/hooks/usePatient';
import useBaseAPIUrl from '../../../helpers/hooks/useBaseAPIUrl';
import useBaseAPIHeaders from '../../../helpers/hooks/useBaseAPIHeaders';
import uploadDocuments from '../../../helpers/requests/uploadDocument';
import { LG_UPLOAD_STAGE } from '../../../pages/lloydGeorgeUploadPage/LloydGeorgeUploadPage';

type Props = {
    documents: Array<UploadDocument>;
    setStage: Dispatch<SetStateAction<LG_UPLOAD_STAGE>>;
    setDocuments: Dispatch<SetStateAction<Array<UploadDocument>>>;
};

function LloydGeorgeUploadStage({ documents, setStage, setDocuments }: Props) {
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const baseUrl = useBaseAPIUrl();
    const baseHeaders = useBaseAPIHeaders();

    const getUploadMessage = (document: UploadDocument) => {
        if (document.state === DOCUMENT_UPLOAD_STATE.SELECTED) return 'Waiting...';
        else if (document.state === DOCUMENT_UPLOAD_STATE.UPLOADING)
            return `${Math.round(document.progress)}% uploaded...`;
        else if (document.state === DOCUMENT_UPLOAD_STATE.SUCCEEDED) return 'Upload successful';
        else if (document.state === DOCUMENT_UPLOAD_STATE.FAILED && document.attempts > 1)
            return 'Upload failed';
        else if (document.state === DOCUMENT_UPLOAD_STATE.FAILED && document.attempts === 1)
            return `${Math.round(document.progress)}% uploaded...`;
        return null;
    };
    const hasFailedUploads = documents.some((d) => !!d.attempts);

    useEffect(() => {
        const hasExceededUploadAttempts = documents.some((d) => d.attempts > 1);
        if (hasExceededUploadAttempts) {
            setDocuments([]);
            setStage(LG_UPLOAD_STAGE.RETRY);
        }
    });

    const retryUpload = async (documents: Array<UploadDocument>) => {
        try {
            await uploadDocuments({
                nhsNumber,
                setDocuments,
                documents,
                baseUrl,
                baseHeaders,
            });
        } catch (e) {}
    };

    return (
        <>
            {hasFailedUploads && (
                <ErrorBox
                    errorBoxSummaryId="failed-uploads"
                    messageTitle="There is a problem with some of your files"
                    messageBody="Some of your files failed to upload, You cannot continue until you retry uploading these files."
                    messageLinkBody="Retry uploading all failed files"
                    errorOnClick={() => {
                        const failedUploads = documents.filter((d) => d.attempts === 1);
                        retryUpload(failedUploads);
                    }}
                />
            )}
            <h1>Uploading record</h1>
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
                    {documents.map((document) => (
                        <Table.Row key={document.id}>
                            <Table.Cell>
                                <div>{document.file.name}</div>
                                {hasFailedUploads && (
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
                                {hasFailedUploads && (
                                    <div style={{ textAlign: 'right' }}>
                                        <LinkButton
                                            onClick={() => {
                                                retryUpload([document]);
                                            }}
                                        >
                                            Retry upload
                                        </LinkButton>
                                    </div>
                                )}
                            </Table.Cell>
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>
        </>
    );
}

export default LloydGeorgeUploadStage;
