import { Button, Select, Table } from 'nhsuk-react-components';
import useTitle from '../../../../helpers/hooks/useTitle';
import {
    DOCUMENT_TYPE,
    SetUploadDocuments,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';
import LinkButton from '../../../generic/linkButton/LinkButton';
import { FieldValues, useForm } from 'react-hook-form';
import { SelectRef } from '../../../../types/generic/selectRef';
import { useNavigate } from 'react-router';
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
type FormData = {
    [key: string]: number | null;
};

const DocumentSelectOrderStage = ({ documents, setDocuments, setMergedPdfBlob }: Props) => {
    const navigate = useNavigate();
    const [errorMessage, setError] = useState('');
    const [previewLoading, setPreviewLoading] = useState(false);

    const documentPositionKey = (documentId: string): string => {
        return `document-${documentId}-position`;
    };

    const getDefaultValues = () => {
        let defaults: FormData = {};

        documents.forEach((doc) => {
            defaults[documentPositionKey(doc.id)] = doc.position!;
        });

        return defaults;
    };

    const { handleSubmit, getValues, register, unregister, formState } = useForm<FormData>({
        reValidateMode: 'onChange',
        shouldFocusError: true,
        defaultValues: getDefaultValues(),
    });

    const scrollToRef = useRef<HTMLDivElement>(null);

    const pageTitle = 'What order do you want these files in?';
    useTitle({ pageTitle });

    const DocumentPositionDropdown = (
        documentId: string,
        currentPosition: number | undefined,
    ): React.JSX.Element => {
        const key = documentPositionKey(documentId);

        const { ref: dropdownInputRef, ...dropdownProps } = register(key, {
            validate: () => {
                const fieldValues = getValues();

                const values = Object.values(fieldValues).map((v) => +v!);

                if (values.some((v) => v === 0)) {
                    setError('Please select a position for every document');
                    scrollToRef.current?.scrollIntoView();
                    return false;
                }

                if (new Set(values).size !== values.length) {
                    setError('Please ensure all documents have a unique position selected');
                    scrollToRef.current?.scrollIntoView();
                    return false;
                }

                return !!fieldValues[key];
            },
            onChange: updateDocumentPositions,
        });

        return (
            <Select
                style={{ minWidth: '25%' }}
                key={key}
                data-testid={key}
                selectRef={dropdownInputRef as SelectRef}
                {...dropdownProps}
                defaultValue={currentPosition}
            >
                <option key={`${documentId}_position_blank`} value=""></option>
                {documents.map((_, index) => {
                    const position = index + 1;
                    return (
                        <option key={`${documentId}_position_${position}`} value={position}>
                            {position}
                        </option>
                    );
                })}
            </Select>
        );
    };

    const onRemove = (index: number) => {
        let updatedDocList: UploadDocument[] = [];
        const key = documentPositionKey(documents[index].id);
        unregister(key);

        if (index >= 0) {
            updatedDocList = [...documents.slice(0, index), ...documents.slice(index + 1)];
        }
        setDocuments(updatedDocList);

        if (updatedDocList.length === 0) {
            navigate(routes.DOCUMENT_UPLOAD);
        }
    };

    const updateDocumentPositions = () => {
        const fieldValues = getValues();

        const updatedDocuments = documents.map((doc) => ({
            ...doc,
            position: fieldValues[documentPositionKey(doc.id)]!,
        }));

        setError('');
        setDocuments(updatedDocuments);
    };

    const submitDocuments = () => {
        updateDocumentPositions();
        if (!errorMessage) {
            navigate(routeChildren.DOCUMENT_UPLOAD_CONFIRMATION);
        }
    };

    const handleErrors = (fields: FieldValues) => {
        const errorMessages = Object.entries(fields).map(
            ([k, v]: [string, { message: string; ref: Element }]) => {
                return {
                    message: v.message,
                    id: v.ref.id,
                };
            },
        );
        setError(errorMessages[0].message);
        scrollToRef.current?.scrollIntoView();
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
                    put your files in the order you need them to appear in the final document by
                    changing the position number
                </li>
                <li>the file marked '1' will be at the start of the final document</li>
            </ul>

            <form
                onSubmit={handleSubmit(submitDocuments, handleErrors)}
                noValidate
                data-testid="upload-document-form"
            >
                {documents && documents.length > 0 && (
                    <>
                        <Table id="selected-documents-table" className="mb-5">
                            <Table.Head>
                                <Table.Row>
                                    <Table.Cell width="45%">Filename</Table.Cell>
                                    <Table.Cell>Pages</Table.Cell>
                                    {/* <Table.Cell>Has pages without OCR</Table.Cell> */}
                                    <Table.Cell
                                        style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}
                                    >
                                        Position
                                    </Table.Cell>
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
                                    return (
                                        <Table.Row key={document.id} id={document.file.name}>
                                            <Table.Cell>
                                                <div>{document.file.name}</div>
                                            </Table.Cell>
                                            <Table.Cell>{document.numPages}</Table.Cell>
                                            {/* <Table.Cell>
                                                {(document.pageInfo?.filter(p => !p).length ?? 0) > 0 ? 'Yes' : 'No'}
                                            </Table.Cell> */}
                                            <Table.Cell>
                                                {DocumentPositionDropdown(
                                                    document.id,
                                                    document.position ?? index + 1,
                                                )}
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

                        {documents.some((doc) => doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE) &&
                            !errorMessage &&
                            formState.isValid && (
                                <>
                                    <h2>Preview this Lloyd George record</h2>
                                    <p>
                                        This shows how the final record will look when combined into
                                        a single document.
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
                    Confirm the file order and continue
                </Button>
            </form>
        </>
    );
};

export default DocumentSelectOrderStage;
