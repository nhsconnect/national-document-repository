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
import { useNavigate } from 'react-router';
import { routeChildren } from '../../../../types/generic/routes';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';
import useTitle from '../../../../helpers/hooks/useTitle';
import { Button, Fieldset, Table, TextInput } from 'nhsuk-react-components';
import { ReactComponent as FileSVG } from '../../../../styles/file-input.svg';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import LinkButton from '../../../generic/linkButton/LinkButton';
import { getDocument } from 'pdfjs-dist';

type Props = {
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

    const documentsValid = () => {
        return (
            documents.length > 0 &&
            documents.every((doc) => doc.state !== DOCUMENT_UPLOAD_STATE.FAILED)
        );
    };

    const pageTitle = () => {
        let title = 'file';

        switch (documentType) {
            case DOCUMENT_TYPE.LLOYD_GEORGE:
                title = 'Lloyd George files';
                break;
        }

        return `Select ${title} to upload`;
    };

    useTitle({ pageTitle: pageTitle() });

    return (
        <>
            <BackButton />
            <h1>{pageTitle()}</h1>

            <div>
                <h2 className="nhsuk-heading-m">Before you upload</h2>
                <p>
                    You can upload files for patients that do not currently have a Lloyd George
                    record stored in this service.
                </p>
                <p>Make sure that all files uploaded are for this patient only.</p>
                <PatientSimpleSummary />
                <p>You can only upload PDF files.</p>
            </div>
            <Fieldset.Legend id="upload-fieldset-legend" size="m">
                Select files to upload
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
                    className={'lloydgeorge_drag-and-drop d-flex'}
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
                            Select files
                        </Button>
                    </div>
                </div>
            </Fieldset>
            {documents && documents.length > 0 && (
                <>
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
                                <Table.Cell style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}>
                                    Filename
                                </Table.Cell>
                                <Table.Cell
                                    width="20%"
                                    style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}
                                >
                                    File size
                                </Table.Cell>
                                <Table.Cell style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}>
                                    Remove file
                                </Table.Cell>
                            </Table.Row>
                        </Table.Head>

                        <Table.Body>
                            {documents.map((document: UploadDocument, index: number) => {
                                return (
                                    <Table.Row key={document.id} id={document.file.name}>
                                        <Table.Cell>
                                            <div>{document.file.name}</div>
                                            {document.error && (
                                                <div style={{ color: 'red' }}>{document.error}</div>
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
                        onClick={() => {
                            navigate(routeChildren.DOCUMENT_UPLOAD_REMOVE_ALL);
                        }}
                    >
                        Remove all
                    </LinkButton>
                </>
            )}
            <div className="lloydgeorge_upload-submission">
                <Button
                    disabled={!documentsValid()}
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
