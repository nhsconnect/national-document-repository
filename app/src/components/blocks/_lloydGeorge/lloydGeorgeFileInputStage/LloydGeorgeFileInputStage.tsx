import React, { Dispatch, SetStateAction, useRef, useState } from 'react';
import BackButton from '../../../generic/backButton/BackButton';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import { TextInput, Button, Fieldset, InsetText, Table } from 'nhsuk-react-components';
import { ReactComponent as FileSVG } from '../../../../styles/file-input.svg';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    FileInputEvent,
    UploadDocument,
    UploadFilesErrors,
} from '../../../../types/pages/UploadDocumentsPage/types';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import usePatient from '../../../../helpers/hooks/usePatient';
import { v4 as uuidv4 } from 'uuid';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import { uploadLloydGeorgeDocumentValidation } from '../../../../helpers/utils/uploadDocumentValidation';
import {
    fileUploadErrorMessages,
    getInlineErrorMessage,
} from '../../../../helpers/utils/fileUploadErrorMessages';
import LinkButton from '../../../generic/linkButton/LinkButton';
import useTitle from '../../../../helpers/hooks/useTitle';

export type Props = {
    documents: Array<UploadDocument>;
    setDocuments: Dispatch<SetStateAction<Array<UploadDocument>>>;
    submitDocuments: () => Promise<void>;
};

function LloydGeorgeFileInputStage({ documents, setDocuments, submitDocuments }: Props) {
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const dob: string = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';
    let fileInputRef = useRef<HTMLInputElement | null>(null);
    const [uploadFilesErrors, setUploadFilesErrors] = useState<Array<UploadFilesErrors>>([]);
    const hasFileInput = !!documents.length;
    const [showNoFilesMessage, setShowNoFilesMessage] = useState<boolean>(false);

    const onSubmit = async () => {
        setShowNoFilesMessage(!hasFileInput);
        setUploadFilesErrors(uploadLloydGeorgeDocumentValidation(documents, patientDetails));
        if (!hasFileInput || uploadFilesErrors.length > 0) {
            window.scrollTo(0, 0);
            return;
        }
        await submitDocuments();
    };

    const updateFileList = (fileArray: File[]) => {
        const documentMap: Array<UploadDocument> = fileArray.map((file) => ({
            id: uuidv4(),
            file,
            state: DOCUMENT_UPLOAD_STATE.SELECTED,
            progress: 0,
            docType: DOCUMENT_TYPE.LLOYD_GEORGE,
            attempts: 0,
        }));
        const updatedDocList = [...documentMap, ...documents];
        setDocuments(updatedDocList);
        setShowNoFilesMessage(false);
        setUploadFilesErrors(uploadLloydGeorgeDocumentValidation(updatedDocList, patientDetails));
    };
    const onFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        let fileArray: File[] = [];
        if (e.dataTransfer.items) {
            [...e.dataTransfer.items].forEach((item) => {
                const file = item.getAsFile();

                if (item.kind === 'file' && file) {
                    fileArray.push(file);
                }
            });
        } else if (e.dataTransfer.files) {
            fileArray = [...e.dataTransfer.files];
        }
        if (fileArray) {
            updateFileList(fileArray);
        }
    };
    const onInput = (e: FileInputEvent) => {
        const fileArray = Array.from(e.target.files ?? new FileList());
        updateFileList(fileArray);
    };
    const onRemove = (index: number) => {
        let updatedDocList: UploadDocument[] = [];
        if (index >= 0) {
            updatedDocList = [...documents.slice(0, index), ...documents.slice(index + 1)];
        }
        setDocuments(updatedDocList);
        setUploadFilesErrors(uploadLloydGeorgeDocumentValidation(updatedDocList, patientDetails));
    };
    const fileErrorMessage = (document: UploadDocument) => {
        const errorsForDocument = uploadFilesErrors.filter(
            (errorFile) => document.file.name === errorFile.filename,
        );
        return errorsForDocument.map((error, index) => (
            <div className="lloydgeorge_file_upload_error" key={document.file.name + index}>
                {getInlineErrorMessage(error)}
            </div>
        ));
    };
    const pageHeader = 'Upload a Lloyd George record';
    useTitle({ pageTitle: pageHeader });
    return (
        <div>
            <BackButton />
            {!!uploadFilesErrors.length && (
                <ErrorBox
                    messageTitle={'There is a problem with some of your files'}
                    errorInputLink={'#nhs-number-input'}
                    errorBoxSummaryId={'error-box-summary'}
                    errorMessageList={uploadFilesErrors}
                    dataTestId="error-box"
                />
            )}
            {showNoFilesMessage && (
                <ErrorBox
                    messageTitle={'There is a problem with some of your files'}
                    messageLinkBody={fileUploadErrorMessages.noFiles.inline}
                    errorBoxSummaryId={'error-box-summary'}
                    errorInputLink={'#upload-lloyd-george'}
                    dataTestId="error-box"
                />
            )}
            <h1>{pageHeader}</h1>
            <div id="patient-info" className="lloydgeorge_record-stage_patient-info">
                <p data-testid="patient-name">
                    {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
                </p>
                <p data-testid="patient-nhs-number">NHS number: {formattedNhsNumber}</p>
                <p data-testid="patient-dob">Date of birth: {dob}</p>
            </div>
            <div>
                <h2 className="nhsuk-heading-m">
                    Before you upload a Lloyd George patient record:
                </h2>
                <ul>
                    <li>The patient details must match the record you are uploading</li>
                    <li>The patient record must be in a PDF file or multiple PDFs</li>
                    <li>Your PDF file(s) should be named in this format:</li>
                    <p className="lg-input-format-paragraph">
                        [PDFnumber]_Lloyd_George_Record_[Patient Name]_[NHS Number]_[D.O.B].PDF
                    </p>
                </ul>
                <InsetText className="input-stage-inset-text">
                    <p>For example:</p>
                    <p>1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].PDF</p>
                    <p>2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].PDF</p>
                </InsetText>
                <p></p>
                <p>
                    It's recommended to upload the entire record in one go, as each file will be
                    combined together based on the file names.
                </p>
                <p>You will not be able to view a partially uploaded record.</p>
            </div>
            <Fieldset.Legend id="upload-fieldset-legend" size="m">
                Select the files you wish to upload
            </Fieldset.Legend>
            <Fieldset>
                <div
                    role="button"
                    id="upload-lloyd-george"
                    tabIndex={0}
                    data-testid="dropzone"
                    onDragOver={(e) => {
                        e.preventDefault();
                    }}
                    onDrop={onFileDrop}
                    className={'lloydgeorge_drag-and-drop'}
                >
                    <strong className="lg-input-bold">
                        Drag and drop a file or multiple files here
                    </strong>
                    <div className="lg-input-svg-display">
                        <FileSVG />
                    </div>
                    <div>
                        <TextInput
                            data-testid={`button-input`}
                            type="file"
                            multiple={true}
                            hidden
                            onChange={(e: FileInputEvent) => {
                                onInput(e);
                                e.target.value = '';
                            }}
                            // @ts-ignore  The NHS Component library is outdated and does not allow for any reference other than a blank MutableRefObject
                            inputRef={(e: HTMLInputElement) => {
                                fileInputRef.current = e;
                            }}
                        />
                        <Button
                            data-testid={`upload-button-input`}
                            type={'button'}
                            className={'nhsuk-button nhsuk-button--secondary bottom-margin'}
                            onClick={() => {
                                fileInputRef.current?.click();
                            }}
                            aria-labelledby="upload-fieldset-legend"
                        >
                            Select files
                        </Button>
                    </div>
                </div>
            </Fieldset>
            {documents && documents.length > 0 && (
                <Table caption="Chosen file(s)" id="selected-documents-table">
                    <Table.Head>
                        <Table.Row>
                            <Table.Cell className="table-cell-lg-input-cell-border">
                                <div className="div-lg-input-cell">
                                    <strong>
                                        {`${documents.length}`} file
                                        {`${documents.length === 1 ? '' : 's'}`} chosen
                                    </strong>
                                </div>
                            </Table.Cell>
                        </Table.Row>
                        <Table.Row>
                            <Table.Cell>Filename</Table.Cell>
                            <Table.Cell>Size</Table.Cell>
                            <Table.Cell>Remove</Table.Cell>
                        </Table.Row>
                    </Table.Head>

                    <Table.Body>
                        {documents.map((document: UploadDocument, index: number) => {
                            return (
                                <Table.Row key={document.id} id={document.file.name}>
                                    <Table.Cell>
                                        <div>{document.file.name}</div>
                                        {fileErrorMessage(document)}
                                    </Table.Cell>
                                    <Table.Cell>{formatFileSize(document.file.size)}</Table.Cell>
                                    <Table.Cell>
                                        <button
                                            type="button"
                                            aria-label={`Remove ${document.file.name} from selection`}
                                            className="link-button"
                                            onClick={() => {
                                                onRemove(index);
                                            }}
                                        >
                                            Remove
                                        </button>
                                    </Table.Cell>
                                </Table.Row>
                            );
                        })}
                    </Table.Body>
                </Table>
            )}
            <div className="lloydgeorge_upload-submission">
                <Button type="button" id="upload-button" onClick={onSubmit}>
                    Upload
                </Button>
                {!!documents.length && (
                    <LinkButton
                        type="button"
                        onClick={() => {
                            onRemove(-1);
                        }}
                    >
                        Remove all
                    </LinkButton>
                )}
            </div>
        </div>
    );
}

export default LloydGeorgeFileInputStage;
