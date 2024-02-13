import React, { Dispatch, SetStateAction } from 'react';
import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import { Table, WarningCallout } from 'nhsuk-react-components';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import { LG_UPLOAD_STAGE } from '../../../pages/lloydGeorgeUploadPage/LloydGeorgeUploadPage';

type Props = {
    documents: Array<UploadDocument>;
    setStage: Dispatch<SetStateAction<LG_UPLOAD_STAGE>>;
};

function LloydGeorgeUploadStage({ documents, setStage }: Props) {
    const getUploadMessage = (document: UploadDocument) => {
        if (document.state === DOCUMENT_UPLOAD_STATE.SELECTED) return 'Waiting...';
        else if (document.state === DOCUMENT_UPLOAD_STATE.UPLOADING)
            return `${Math.round(document.progress)}% uploaded...`;
        else if (document.state === DOCUMENT_UPLOAD_STATE.SUCCEEDED) return 'Upload successful';
        else if (document.state === DOCUMENT_UPLOAD_STATE.FAILED) return 'Upload failed';
    };
    return (
        <>
            <button
                onClick={() => {
                    setStage(LG_UPLOAD_STAGE.COMPLETE);
                }}
            >
                next stage
            </button>
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
            >
                <Table.Head role="rowgroup">
                    <Table.Row>
                        <Table.Cell>Filename</Table.Cell>
                        <Table.Cell style={{ width: '140px' }}>Size</Table.Cell>
                        <Table.Cell style={{ width: '200px' }}>Upload Progress</Table.Cell>
                    </Table.Row>
                </Table.Head>
                <Table.Body>
                    {documents.map((document) => (
                        <Table.Row key={document.id}>
                            <Table.Cell>{document.file.name}</Table.Cell>
                            <Table.Cell style={{ width: '140px' }}>
                                {formatFileSize(document.file.size)}
                            </Table.Cell>
                            <Table.Cell style={{ width: '200px' }}>
                                <progress
                                    aria-label={`Uploading ${document.file.name}`}
                                    max="100"
                                    value={document.progress}
                                ></progress>
                                <p role="status" aria-label={`${document.file.name} upload status`}>
                                    {getUploadMessage(document)}
                                </p>
                            </Table.Cell>
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table>
        </>
    );
}

export default LloydGeorgeUploadStage;
