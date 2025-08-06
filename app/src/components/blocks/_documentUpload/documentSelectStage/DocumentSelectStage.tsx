import { useRef } from 'react';
import {
    DOCUMENT_TYPE,
    DOCUMENT_UPLOAD_STATE,
    FileInputEvent,
    SetUploadDocuments,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { v4 as uuidv4 } from 'uuid';
import BackButton from '../../../generic/backButton/BackButton';
import { useNavigate } from 'react-router-dom';
import { routeChildren, routes } from '../../../../types/generic/routes';
import useTitle from '../../../../helpers/hooks/useTitle';
import { Button, Fieldset, Table, TextInput } from 'nhsuk-react-components';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import LinkButton from '../../../generic/linkButton/LinkButton';
import { getDocument } from 'pdfjs-dist';
import PatientSummary, { PatientInfo } from '../../../generic/patientSummary/PatientSummary';

export type Props = {
    setDocuments: SetUploadDocuments;
    documents: Array<UploadDocument>;
    documentType: DOCUMENT_TYPE;
};

const DocumentSelectStage = ({ documents, setDocuments, documentType }: Props) => {
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const navigate = useNavigate();

    const validateFileType = (file: File): boolean => {
        switch (documentType) {
            case DOCUMENT_TYPE.LLOYD_GEORGE:
                return file.type === 'application/pdf';
        }

        return true;
    };

    const onFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();

        let fileArray: File[] = [];
        if (e.dataTransfer.items?.length > 0) {
            [...e.dataTransfer.items].forEach((item) => {
                const file = item.getAsFile();

                if (item.kind === 'file' && file) {
                    fileArray.push(file);
                }
            });
        } else if (e.dataTransfer.files?.length > 0) {
            fileArray = [...e.dataTransfer.files];
        }

        if (fileArray) {
            void updateFileList(fileArray.filter(validateFileType));
        }
    };

    const onInput = (e: FileInputEvent) => {
        const fileArray = Array.from(e.target.files ?? new FileList()).filter(validateFileType);

        void updateFileList(fileArray);
    };

    const updateFileList = async (fileArray: File[]) => {
        const documentMap = fileArray
            .filter((f) => !documents.some((d) => d.file.name === f.name))
            .map(async (file) => {
                const document: UploadDocument = {
                    id: uuidv4(),
                    file,
                    state: DOCUMENT_UPLOAD_STATE.SELECTED,
                    progress: 0,
                    docType: documentType,
                    attempts: 0,
                    numPages: 0,
                };

                const buffer = await file.arrayBuffer();

                try {
                    const pdf = await getDocument(buffer).promise;
                    await pdf.getPage(1);
                    document.numPages = pdf.numPages;
                    await pdf.destroy();
                } catch (e) {
                    const error = e as Error;
                    document.state = DOCUMENT_UPLOAD_STATE.FAILED;

                    let errorMessage = 'Failed to read PDF.';
                    if (error.message.startsWith('Invalid PDF')) {
                        errorMessage = 'PDF Invalid.';
                    } else if (error.message.includes('password')) {
                        errorMessage = 'PDF is password protected.';
                    }
                    document.error = `${errorMessage} Please remove this file to continue with the upload.`;
                }

                return document;
            });

        const docs = await Promise.all(documentMap);

        updateDocuments([...docs, ...documents]);
    };

    const onRemove = (index: number) => {
        let updatedDocList: UploadDocument[] = [];
        if (index >= 0) {
            updatedDocList = [...documents.slice(0, index), ...documents.slice(index + 1)];
        }

        updateDocuments(updatedDocList);
    };

    const updateDocuments = (docs: UploadDocument[]) => {
        const sortedDocs = docs
            .sort((a, b) => a.file.lastModified - b.file.lastModified)
            .map((doc, index) => ({
                ...doc,
                position: index + 1,
            }));

        setDocuments(sortedDocs);
    };

    const allowedFileTypes = () => {
        switch (documentType) {
            case DOCUMENT_TYPE.LLOYD_GEORGE:
                return '.pdf';
        }

        return '';
    };

    // const documentsValid = () => {
    //     return (
    //         documents.length > 0 &&
    //         documents.every((doc) => doc.state !== DOCUMENT_UPLOAD_STATE.FAILED)
    //     );
    // };

    const pageTitle = () => {
        let title = 'files';

        switch (documentType) {
            case DOCUMENT_TYPE.LLOYD_GEORGE:
                title = 'Lloyd George files';
                break;
        }

        return `Choose ${title} to upload`;
    };

    useTitle({ pageTitle: pageTitle() });

    return (
        <>
            <BackButton toLocation={routes.VERIFY_PATIENT} dataTestid="back-button" />
            <h1>{pageTitle()}</h1>

            <div>
                <h2 className="nhsuk-heading-m">Before you upload</h2>
                <ul>
                    <li>you can only upload PDF files</li>
                    <li>only upload files that are part of this patient's Lloyd George record</li>
                    <li>remove any passwords from files</li>
                </ul>
                <p>
                    Uploading may take longer if there are many files or if individual files are
                    larger
                </p>

                <div className="nhsuk-inset-text">
                    <p>Make sure that all files uploaded are for this patient only:</p>
                    <PatientSummary>
                        <PatientSummary.Child item={PatientInfo.FULL_NAME} />
                        <PatientSummary.Child item={PatientInfo.NHS_NUMBER} />
                        <PatientSummary.Child item={PatientInfo.BIRTH_DATE} />
                    </PatientSummary>
                </div>

                <p>You can only upload PDF files.</p>
            </div>
            <Fieldset.Legend id="upload-fieldset-legend" size="m">
                Choose PDF files to upload
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
                    <div>
                        <TextInput
                            data-testid={`button-input`}
                            type="file"
                            multiple={true}
                            hidden
                            accept={allowedFileTypes()}
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
                            Choose PDF files
                        </Button>
                    </div>
                </div>
            </Fieldset>
            {documents && documents.length > 0 && (
                <>
                    <Table caption="Chosen files" id="selected-documents-table">
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
                                <Table.Cell className="word-break-keep-all">Filename</Table.Cell>
                                <Table.Cell width="20%" className="word-break-keep-all">
                                    File size
                                </Table.Cell>
                                <Table.Cell className="word-break-keep-all">Remove file</Table.Cell>
                            </Table.Row>
                        </Table.Head>

                        <Table.Body>
                            {documents.map((document: UploadDocument, index: number) => {
                                return (
                                    <Table.Row key={document.id} id={document.file.name}>
                                        <Table.Cell>
                                            <div>
                                                <strong>{document.file.name}</strong>
                                            </div>
                                            {document.error && (
                                                <div className="nhs-warning-color">
                                                    {document.error}
                                                </div>
                                            )}
                                        </Table.Cell>
                                        <Table.Cell>
                                            {formatFileSize(document.file.size)}
                                        </Table.Cell>
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
                    <LinkButton
                        type="button"
                        className="remove-all-button mb-5"
                        data-testid="remove-all-button"
                        onClick={() => {
                            navigate(routeChildren.DOCUMENT_UPLOAD_REMOVE_ALL);
                        }}
                    >
                        Remove all files
                    </LinkButton>
                </>
            )}
            <div className="lloydgeorge_upload-submission">
                <Button
                    type="button"
                    id="upload-button"
                    onClick={() => navigate(routeChildren.DOCUMENT_UPLOAD_SELECT_ORDER)}
                >
                    Continue
                </Button>
            </div>
        </>
    );
};

export default DocumentSelectStage;
