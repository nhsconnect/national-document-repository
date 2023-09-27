import { Input, Table, WarningCallout } from 'nhsuk-react-components';
import React from 'react';
import {
    DOCUMENT_TYPE,
    FileInputEvent,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import { FieldValues, UseControllerReturn } from 'react-hook-form';

type Props = {
    documents: Array<UploadDocument>;
    formController: UseControllerReturn<FieldValues, string>;
    inputRef: React.MutableRefObject<HTMLInputElement | null>;
    onDocumentRemove: (index: number, docType: DOCUMENT_TYPE) => void;
    onDocumentInput: (e: FileInputEvent, docType: DOCUMENT_TYPE) => void;
    formType: DOCUMENT_TYPE;
    showHelp?: boolean;
};

const DocumentInputForm = ({
    documents,
    onDocumentRemove,
    onDocumentInput,
    formController,
    inputRef,
    formType,
    showHelp = false,
}: Props) => {
    const hasDuplicateFiles = documents.some((doc: UploadDocument) => {
        return documents.some(
            (compare: UploadDocument) =>
                doc.file.name === compare.file.name &&
                doc.file.size === compare.file.size &&
                doc.id !== compare.id,
        );
    });
    return (
        <>
            <Input
                data-testid={`${formType}-input`}
                id={`${formType}-documents-input`}
                label="Select file(s)"
                type="file"
                multiple={true}
                name={formController.field.name}
                error={formController.fieldState.error?.message}
                onChange={(e: FileInputEvent) => onDocumentInput(e, formType)}
                onBlur={formController.field.onBlur}
                // @ts-ignore  The NHS Component library is outdated and does not allow for any reference other than a blank MutableRefObject
                inputRef={(e: HTMLInputElement) => {
                    formController.field.ref(e);
                    inputRef.current = e;
                }}
                //@ts-ignore
                hint={
                    <ul>
                        <li>
                            {formType === DOCUMENT_TYPE.LLOYD_GEORGE
                                ? 'If you are uploading a patient’s Lloyd George envelope you must upload the full Lloyd George envelope including the front and back of the envelope.'
                                : "A patient's full electronic health record including attachments must be uploaded."}
                        </li>
                        <li>You can select multiple files to upload at once.</li>
                        {showHelp && (
                            <li>
                                In the event documents cannot be uploaded, they must be printed and
                                sent via{' '}
                                <a
                                    href="https://secure.pcse.england.nhs.uk/"
                                    target="_blank"
                                    rel="noreferrer"
                                >
                                    Primary Care Support England
                                </a>
                                .
                            </li>
                        )}
                        {formType === DOCUMENT_TYPE.LLOYD_GEORGE && (
                            <>
                            <li>
                                Each Lloyd George file uploaded must match the following format: [PDFnumber]_Lloyd_George_Record_[Patient Name]_[NHS Number]_[D.O.B]. For example: 1of2_Lloyd_George_Record_[Joe Bloggs]_[123456789]_[25-12-2019]
                            </li>
                            <li>
                                You can only upload PDF files
                            </li>
                            </>
                        )}
                    </ul>
                }
            />
            <div role="region" aria-live="polite">
                {documents && documents.length > 0 && (
                    <Table caption="Selected documents" id="selected-documents-table">
                        <Table.Head>
                            <Table.Row>
                                <Table.Cell>Filename</Table.Cell>
                                <Table.Cell>Size</Table.Cell>
                                <Table.Cell>Remove</Table.Cell>
                            </Table.Row>
                        </Table.Head>

                        <Table.Body>
                            {documents.map((document: UploadDocument, index: number) => (
                                <Table.Row key={document.id}>
                                    <Table.Cell>{document.file.name}</Table.Cell>
                                    <Table.Cell>{formatFileSize(document.file.size)}</Table.Cell>
                                    <Table.Cell>
                                        <button
                                            type="button"
                                            aria-label={`Remove ${document.file.name} from selection`}
                                            className="link-button"
                                            onClick={() => {
                                                onDocumentRemove(index, formType);
                                            }}
                                        >
                                            Remove
                                        </button>
                                    </Table.Cell>
                                </Table.Row>
                            ))}
                        </Table.Body>
                    </Table>
                )}
                {hasDuplicateFiles && (
                    <WarningCallout>
                        <WarningCallout.Label>Possible duplicate file</WarningCallout.Label>
                        <p>There are two or more documents with the same name.</p>
                        <p>Are you sure you want to proceed?</p>
                    </WarningCallout>
                )}
            </div>
        </>
    );
};

export default DocumentInputForm;
