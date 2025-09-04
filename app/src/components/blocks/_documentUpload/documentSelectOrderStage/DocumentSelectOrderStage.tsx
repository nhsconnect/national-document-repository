import { Button, Table } from 'nhsuk-react-components';
import useTitle from '../../../../helpers/hooks/useTitle';
import {
    DOCUMENT_TYPE,
    SetUploadDocuments,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';
import LinkButton from '../../../generic/linkButton/LinkButton';
import { useNavigate } from 'react-router-dom';
import BackButton from '../../../generic/backButton/BackButton';
import { Dispatch, SetStateAction, useEffect, useRef, useState } from 'react';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import { routeChildren, routes } from '../../../../types/generic/routes';
import DocumentUploadLloydGeorgePreview from '../documentUploadLloydGeorgePreview/DocumentUploadLloydGeorgePreview';
import React from 'react';

type Props = {
    documents: UploadDocument[];
    setDocuments: SetUploadDocuments;
    setMergedPdfBlob: Dispatch<SetStateAction<Blob | undefined>>;
};

const DocumentSelectOrderStage = ({ documents, setDocuments, setMergedPdfBlob }: Props) => {
    const navigate = useNavigate();
    const [errorMessage, setError] = useState('');
    const [previewLoading, setPreviewLoading] = useState(false);

    // Drag and Drop state
    const [draggedItem, setDraggedItem] = useState<string | null>(null);
    const [dragOverItem, setDragOverItem] = useState<string | null>(null);

    const scrollToRef = useRef<HTMLDivElement>(null);

    const pageTitle = 'What order do you want these files in?';
    useTitle({ pageTitle });

    const formatLastModified = (lastModified: number): string => {
        const date = new Date(lastModified);
        return date.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const handleDragStart = (e: React.DragEvent<HTMLTableRowElement>, documentId: string) => {
        setDraggedItem(documentId);

        // Set drag effect and data
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', documentId);

        // Add visual feedback
        e.currentTarget.style.opacity = '0.5';
    };

    const handleDragEnd = (e: React.DragEvent<HTMLTableRowElement>) => {
        setDraggedItem(null);
        setDragOverItem(null);

        // Reset visual feedback
        e.currentTarget.style.opacity = '1';
    };

    const handleDragOver = (e: React.DragEvent<HTMLTableRowElement>) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    };

    const handleDragEnter = (e: React.DragEvent<HTMLTableRowElement>, documentId: string) => {
        e.preventDefault();
        if (draggedItem !== documentId) {
            setDragOverItem(documentId);
        }
    };

    const handleDragLeave = (e: React.DragEvent<HTMLTableRowElement>) => {
        e.preventDefault();
        setDragOverItem(null);
    };

    const handleDrop = (e: React.DragEvent<HTMLTableRowElement>, targetDocumentId: string) => {
        e.preventDefault();

        if (!draggedItem || draggedItem === targetDocumentId) {
            return;
        }

        const reorderedDocuments = reorderDocuments(draggedItem, targetDocumentId);
        setDocuments(reorderedDocuments);
        updateFormWithNewPositions(reorderedDocuments);

        setDraggedItem(null);
        setDragOverItem(null);
    };

    const reorderDocuments = (draggedId: string, targetId: string): UploadDocument[] => {
        const draggedIndex = documents.findIndex((doc) => doc.id === draggedId);
        const targetIndex = documents.findIndex((doc) => doc.id === targetId);

        if (draggedIndex === -1 || targetIndex === -1) {
            return documents;
        }

        const reordered = [...documents];
        const [draggedDoc] = reordered.splice(draggedIndex, 1);
        reordered.splice(targetIndex, 0, draggedDoc);

        // Update positions to be sequential
        return reordered.map((doc, index) => ({
            ...doc,
            position: index + 1,
        }));
    };

    const updateFormWithNewPositions = (reorderedDocs: UploadDocument[]) => {
        // Since we're not using React Hook Form anymore, we just need to clear errors
        setError(''); // Clear any existing errors
    };
    const handleKeyDown = (e: React.KeyboardEvent<HTMLTableRowElement>, index: number) => {
        if (!e.ctrlKey && !e.metaKey) return;

        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault();
                moveDocument(index, index - 1);
                break;
            case 'ArrowDown':
                e.preventDefault();
                moveDocument(index, index + 1);
                break;
        }
    };

    const moveDocument = (fromIndex: number, toIndex: number) => {
        if (toIndex < 0 || toIndex >= documents.length) return;

        const reordered = [...documents];
        const [movedDoc] = reordered.splice(fromIndex, 1);
        reordered.splice(toIndex, 0, movedDoc);

        const updatedDocs = reordered.map((doc, index) => ({
            ...doc,
            position: index + 1,
        }));

        setDocuments(updatedDocs);
        updateFormWithNewPositions(updatedDocs);
    };

    const orderNumerically = () => {
        const sortedDocuments = [...documents].sort((a, b) => {
            const extractNumbers = (filename: string): number[] => {
                const matches = filename.match(/\d+/g);
                return matches ? matches.map(Number) : [];
            };

            const aNumbers = extractNumbers(a.file.name);
            const bNumbers = extractNumbers(b.file.name);

            // Compare each number position by position
            for (let i = 0; i < Math.max(aNumbers.length, bNumbers.length); i++) {
            const aNum = aNumbers[i] || 0;
            const bNum = bNumbers[i] || 0;
            
            if (aNum !== bNum) {
                return aNum - bNum;
            }
            }

            // If all numbers are equal, fallback to alphabetical
            return a.file.name.localeCompare(b.file.name, 'en', { sensitivity: 'base' });
        });

        const updatedDocs = sortedDocuments.map((doc, index) => ({
            ...doc,
            position: index + 1,
        }));

        setDocuments(updatedDocs);
        updateFormWithNewPositions(updatedDocs);
    };

    const orderAlphabetically = () => {
        const sortedDocuments = [...documents].sort((a, b) =>
            a.file.name.localeCompare(b.file.name, 'en', { sensitivity: 'base' }),
        );

        const updatedDocs = sortedDocuments.map((doc, index) => ({
            ...doc,
            position: index + 1,
        }));

        setDocuments(updatedDocs);
        updateFormWithNewPositions(updatedDocs);
    };

    const orderByLastModified = () => {
        const sortedDocuments = [...documents].sort(
            (a, b) => b.file.lastModified - a.file.lastModified,
        );

        const updatedDocs = sortedDocuments.map((doc, index) => ({
            ...doc,
            position: index + 1,
        }));

        setDocuments(updatedDocs);
        updateFormWithNewPositions(updatedDocs);
    };

    const reverseOrder = () => {
        const reversedDocuments = [...documents].reverse();

        const updatedDocs = reversedDocuments.map((doc, index) => ({
            ...doc,
            position: index + 1,
        }));

        setDocuments(updatedDocs);
        updateFormWithNewPositions(updatedDocs);
    };

    const onRemove = (index: number) => {
        let updatedDocList: UploadDocument[] = [];

        if (index >= 0) {
            updatedDocList = [...documents.slice(0, index), ...documents.slice(index + 1)];
        }

        const updatedDocListWithPositions = updatedDocList.map((doc, newIndex) => ({
            ...doc,
            position: newIndex + 1,
        }));

        setDocuments(updatedDocListWithPositions);

        if (updatedDocListWithPositions.length === 0) {
            navigate(routes.DOCUMENT_UPLOAD);
        }
    };

    const submitDocuments = () => {
        // Ensure all documents have valid positions
        const hasValidPositions = documents.every((doc) => doc.position && doc.position > 0);

        if (!hasValidPositions) {
            setError('Please ensure all documents have valid positions');
            scrollToRef.current?.scrollIntoView();
            return;
        }

        if (!errorMessage) {
            navigate(routeChildren.DOCUMENT_UPLOAD_CONFIRMATION);
        }
    };

    useEffect(() => {
        if (documents.length === 0) {
            navigate(routes.DOCUMENT_UPLOAD);
            return;
        }
    }, [navigate, documents.length]);

    return (
        <>
            <BackButton />
            <h1>{pageTitle}</h1>
            <PatientSimpleSummary />

            {errorMessage && (
                <ErrorBox
                    dataTestId="error-box"
                    errorBoxSummaryId="document-positions"
                    messageTitle="There is a problem"
                    messageBody={errorMessage}
                    scrollToRef={scrollToRef}
                />
            )}

            <p>When you upload your files, they will be combined into a single PDF document.</p>

            <p>Your files are not currently in order:</p>
            <ul>
                <li>
                    drag and drop rows to reorder your files, or use Ctrl+Arrow keys when focused on
                    a row
                </li>
                <li>the file marked '1' will be at the start of the final document</li>
            </ul>

            {documents && documents.length > 0 && (
                <div className="drag-instructions">
                    <p>
                        <strong>Tip:</strong> You can drag and drop rows to reorder your files, or
                        use Ctrl+Arrow keys when focused on a row.
                    </p>
                    {/* <p> */}
                    <strong>Ordering:</strong> These will order the entire list based on file name.
                    {/* </p> */}
                    <div className="d-flex">
                        <button
                            type="button"
                            onClick={orderAlphabetically}
                            disabled={previewLoading}
                            className="link-button ml-2"
                            style={{ fontSize: '14px', padding: '8px 16px' }}
                        >
                            A-Z
                        </button>
                        <button
                            type="button"
                            onClick={orderNumerically}
                            disabled={previewLoading}
                            className="link-button ml-2"
                            style={{ fontSize: '14px', padding: '8px 16px' }}
                        >
                            0-9
                        </button>
                        <button
                            type="button"
                            onClick={orderByLastModified}
                            disabled={previewLoading}
                            className="link-button"
                            style={{ fontSize: '14px', padding: '8px 16px' }}
                        >
                            Last Modified
                        </button>
                        <button
                            type="button"
                            onClick={reverseOrder}
                            disabled={previewLoading}
                            className="link-button"
                            style={{ fontSize: '14px', padding: '8px 16px' }}
                        >
                            Reverse Order
                        </button>
                    </div>
                </div>
            )}

            <form
                onSubmit={(e) => {
                    e.preventDefault();
                    submitDocuments();
                }}
                noValidate
                data-testid="upload-document-form"
            >
                {documents && documents.length > 0 && (
                    <>
                        <Table id="selected-documents-table" className="mb-5">
                            <Table.Head>
                                <Table.Row>
                                    <Table.Cell width="5%">#</Table.Cell>
                                    <Table.Cell width="30%">Filename</Table.Cell>
                                    <Table.Cell>Pages</Table.Cell>
                                    <Table.Cell>Position</Table.Cell>
                                    <Table.Cell>Last Modified</Table.Cell>
                                    <Table.Cell
                                        style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}
                                    >
                                        View file
                                    </Table.Cell>
                                    <Table.Cell
                                        style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}
                                    >
                                        Remove file
                                    </Table.Cell>
                                </Table.Row>
                            </Table.Head>

                            <Table.Body>
                                {documents.map((document: UploadDocument, index: number) => {
                                    const isDraggedItem = draggedItem === document.id;
                                    const isDragOver = dragOverItem === document.id;

                                    return (
                                        <Table.Row
                                            key={document.id}
                                            id={document.file.name}
                                            className={`drag-table-row ${isDraggedItem ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                                            draggable={true}
                                            onDragStart={(e) => handleDragStart(e, document.id)}
                                            onDragEnd={handleDragEnd}
                                            onDragOver={handleDragOver}
                                            onDragEnter={(e) => handleDragEnter(e, document.id)}
                                            onDragLeave={handleDragLeave}
                                            onDrop={(e) => handleDrop(e, document.id)}
                                            onKeyDown={(e) => handleKeyDown(e, index)}
                                            aria-grabbed={isDraggedItem ? 'true' : 'false'}
                                            aria-dropeffect={isDragOver ? 'move' : 'none'}
                                            aria-label={`Document row for ${document.file.name}`}
                                            role="row"
                                            tabIndex={0}
                                        >
                                            <Table.Cell className="drag-handle">
                                                <div
                                                    aria-label={`Drag to reorder ${document.file.name}`}
                                                >
                                                    ⋮⋮
                                                </div>
                                            </Table.Cell>
                                            <Table.Cell>
                                                <div>{document.file.name}</div>
                                            </Table.Cell>
                                            <Table.Cell>{document.numPages}</Table.Cell>
                                            <Table.Cell>
                                                <span className="position-indicator">
                                                    {document.position ?? index + 1}
                                                </span>
                                            </Table.Cell>
                                            <Table.Cell>
                                                {formatLastModified(document.file.lastModified)}
                                            </Table.Cell>
                                            <Table.Cell>
                                                <a
                                                    href={URL.createObjectURL(document.file)}
                                                    aria-label="Preview - opens in a new tab"
                                                    target="_blank"
                                                    rel="noreferrer"
                                                >
                                                    View
                                                </a>
                                            </Table.Cell>
                                            <Table.Cell>
                                                <button
                                                    type="button"
                                                    aria-label={`Remove ${document.file.name} from selection`}
                                                    className="link-button"
                                                    disabled={previewLoading}
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

                        {documents.length > 1 && (
                            <div className="lloydgeorge_upload-submission pb-5">
                                <LinkButton
                                    type="button"
                                    onClick={() => {
                                        navigate(routeChildren.DOCUMENT_UPLOAD_REMOVE_ALL);
                                    }}
                                    disabled={previewLoading}
                                >
                                    Remove all
                                </LinkButton>
                            </div>
                        )}

                        {/* Preview Section */}
                        {documents.some((doc) => doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE) &&
                            !errorMessage && (
                                <>
                                    <h2>Preview this Lloyd George record</h2>
                                    <p>
                                        This shows how the final record will look when combined into
                                        a single document.
                                    </p>
                                    <p>
                                        Preview may take longer to load if there are many files or
                                        if individual files are large. a single document.
                                    </p>
                                    <DocumentUploadLloydGeorgePreview
                                        documents={documents
                                            .filter(
                                                (doc) => doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE,
                                            )
                                            .sort((a, b) => a.position! - b.position!)}
                                        previewLoading={previewLoading}
                                        setPreviewLoading={setPreviewLoading}
                                        setMergedPdfBlob={setMergedPdfBlob}
                                    />
                                </>
                            )}
                    </>
                )}
                <Button
                    type="submit"
                    id="form-submit"
                    data-testid="form-submit-button"
                    className="mt-4"
                    disabled={previewLoading}
                >
                    Continue
                </Button>
            </form>
        </>
    );
};

export default DocumentSelectOrderStage;
