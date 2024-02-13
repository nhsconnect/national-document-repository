import React from 'react';
import { buildDocument, buildTextFile } from '../../../helpers/test/testBuilders';
import { DOCUMENT_UPLOAD_STATE } from '../../../types/pages/UploadDocumentsPage/types';
import { Table } from 'nhsuk-react-components';
import formatFileSize from '../../../helpers/utils/formatFileSize';

type Props = {};

function LloydGeorgeUploadStage({}: Props) {
    const files = [buildTextFile('one', 100), buildTextFile('two', 101)];
    const documents = files.map((file) => buildDocument(file, DOCUMENT_UPLOAD_STATE.SUCCEEDED));
    const getUploadMessage = (type: DOCUMENT_UPLOAD_STATE) => {
        if (type === DOCUMENT_UPLOAD_STATE.SELECTED) return 'Waiting...';
        else if (type === DOCUMENT_UPLOAD_STATE.UPLOADING) return 'Uploading...';
        else if (type === DOCUMENT_UPLOAD_STATE.SUCCEEDED) return 'Uploaded';
        else if (type === DOCUMENT_UPLOAD_STATE.FAILED) return 'Upload failed';
    };
    return (
        <Table
            responsive
            caption="Your documents are uploading"
            captionProps={{
                className: 'nhsuk-u-visually-hidden',
            }}
        >
            <Table.Head role="rowgroup">
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
                            <p role="status" aria-label={`${document.file.name} upload status`}>
                                {document.state === DOCUMENT_UPLOAD_STATE.UPLOADING ? (
                                    <> {Math.round(document.progress)}% uploaded... </>
                                ) : (
                                    <>{getUploadMessage(document.state)}</>
                                )}
                            </p>
                        </Table.Cell>
                    </Table.Row>
                ))}
            </Table.Body>
        </Table>
    );
}

export default LloydGeorgeUploadStage;
