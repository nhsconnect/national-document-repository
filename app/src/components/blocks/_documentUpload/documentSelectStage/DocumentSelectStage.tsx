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
import { routeChildren, routes } from '../../../../types/generic/routes';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';
import useTitle from '../../../../helpers/hooks/useTitle';
import { Button, Fieldset, Table, TextInput } from 'nhsuk-react-components';
import { ReactComponent as FileSVG } from '../../../../styles/file-input.svg';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import LinkButton from '../../../generic/linkButton/LinkButton';

type Props = {
    setDocuments: SetUploadDocuments;
    documents: Array<UploadDocument>;
    documentType: DOCUMENT_TYPE;
};

const DocumentSelectStage = ({ documents, setDocuments, documentType }: Props) => {
    const fileInputRef = useRef<HTMLInputElement | null>(null);

    const hasFileInput = documents.length > 0;

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
            updateFileList(fileArray.filter(validateFileType));
        }
    };

    const onInput = (e: FileInputEvent) => {
        const fileArray = Array.from(e.target.files ?? new FileList()).filter(validateFileType);

        updateFileList(fileArray);
    };

    const updateFileList = (fileArray: File[]) => {
        const documentMap: Array<UploadDocument> = fileArray
            .filter((f) => !documents.some((d) => d.file.name === f.name))
            .map((file) => ({
                id: uuidv4(),
                file,
                state: DOCUMENT_UPLOAD_STATE.SELECTED,
                progress: 0,
                docType: documentType,
                attempts: 0,
            }));
        const updatedDocList = [...documentMap, ...documents].sort(
            (a, b) => a.file.lastModified - b.file.lastModified,
        );
        setDocuments(updatedDocList);
    };

    const onRemove = (index: number) => {
        let updatedDocList: UploadDocument[] = [];
        if (index >= 0) {
            updatedDocList = [...documents.slice(0, index), ...documents.slice(index + 1)];
        }
        setDocuments(updatedDocList);
    };

    const allowedFileTypes = () => {
        switch (documentType) {
            case DOCUMENT_TYPE.LLOYD_GEORGE:
                return '.pdf';
        }

        return '';
    };

    const pageTitle = () => {
        let title = 'file';

        switch (documentType) {
            case DOCUMENT_TYPE.LLOYD_GEORGE:
                title = 'Lloyd George documents';
                break;
        }

        return `Select ${title} to upload for this patient`;
    };

    useTitle({ pageTitle: pageTitle() });

    return (
        <>
            <BackButton />
            <h1>{pageTitle()}</h1>
            <PatientSimpleSummary />

            <div>
                <h2 className="nhsuk-heading-m">Before you upload</h2>
                <p>
                    This feature is used for uploading documents where a patient doesn't already
                    have a record in this service that you want to be added{' '}
                    <i>
                        or to upload a record that will replace/create a newer version of the record
                        for this patient. This is usually done when a record needs to be corrected
                        for example if documents are found to be belonging to another patient.
                    </i>
                </p>
                <p>
                    You cannot add documents to an existing document of the same type without
                    replacing the original.
                </p>
                <p>
                    There are scanning standards that must be adhered to. Ensure documents are
                    compliant before uploading. The Scanning Standards can be found{' '}
                    <a target="_blank">here.</a>
                </p>
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
                                    File name
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
                        style={{ paddingLeft: 0, paddingBottom: '25px' }}
                        onClick={() => {
                            onRemove(-1);
                        }}
                    >
                        Remove all
                    </LinkButton>
                </>
            )}
            <div className="lloydgeorge_upload-submission">
                <Button
                    disabled={!hasFileInput}
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
