import { BackLink, Button, Select, Table } from 'nhsuk-react-components';
import useTitle from '../../../../helpers/hooks/useTitle';
import {
    DOCUMENT_TYPE,
    SetUploadDocuments,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';
import LinkButton from '../../../generic/linkButton/LinkButton';
import { useForm } from 'react-hook-form';
import _ from 'cypress/types/lodash';
import { SelectRef } from '../../../../types/generic/selectRef';
import { useNavigate } from 'react-router';
import BackButton from '../../../generic/backButton/BackButton';
import { useRef, useState } from 'react';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import { routeChildren } from '../../../../types/generic/routes';
import DocumentUploadLloydGeorgePreview from '../documentUploadLloydGeorgePreview/DocumentUploadLloydGeorgePreview';

type Props = {
    documents: UploadDocument[];
    setDocuments: SetUploadDocuments;
};

const DocumentSelectOrderStage = ({ documents, setDocuments }: Props) => {
    const navigate = useNavigate();
    const [errorMessage, setError] = useState('');

    const { handleSubmit, getValues, formState, register } = useForm();

    const scrollToRef = useRef<HTMLDivElement>(null);

    const pageTitle = 'What order do you want these files in?';
    useTitle({ pageTitle });

    const documentPositionKey = (documentId: string): string => {
        return `document-${documentId}-position`;
    };

    const DocumentPositionDropdown = (
        documentId: string,
        currentPosition: number | undefined,
    ): JSX.Element => {
        const key = documentPositionKey(documentId);

        const { ref: dropdownInputRef, ...dropdownProps } = register(key, {
            required: 'Required',
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
                <option key={`${documentId}_position_blank`}></option>
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
        if (index >= 0) {
            updatedDocList = [...documents.slice(0, index), ...documents.slice(index + 1)];
        }
        setDocuments(updatedDocList);
    };

    const updateDocumentPositions = () => {
        const fieldValues = getValues();
        const values = Object.values(fieldValues);

        if (new Set(values).size !== values.length) {
            setError('Please ensure all documents have a unique position selected');
            scrollToRef.current?.scrollIntoView();
            return;
        }

        const updatedDocuments = documents.map((d) => {
            d.position = fieldValues[documentPositionKey(d.id)];
            return d;
        });

        setError('');
        setDocuments(updatedDocuments);
    };

    const submitDocuments = () => {
        updateDocumentPositions();
        navigate(routeChildren.DOCUMENT_UPLOAD_CONFIRMATION);
    };

    const handleErrors = () => {
        setError('Please select a position for every document');
        scrollToRef.current?.scrollIntoView();
    };

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

            <p>
                Enter the number each file will sit in, in the digitised Lloyd George record with 1
                being the first file at the start of the PDF.
            </p>
            <form
                onSubmit={handleSubmit(submitDocuments, handleErrors)}
                noValidate
                data-testid="upload-document-form"
            >
                {documents && documents.length > 0 && (
                    <>
                        <Table id="selected-documents-table">
                            <Table.Head>
                                <Table.Row>
                                    <Table.Cell width="45%">Filename</Table.Cell>
                                    <Table.Cell
                                        style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}
                                    >
                                        Position
                                    </Table.Cell>
                                    <Table.Cell
                                        style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}
                                    >
                                        Preview file
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
                                                >
                                                    Preview file
                                                </a>
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

                        {documents.some((doc) => doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE) &&
                            formState.isValid && (
                                <>
                                    <h2>Stitched Lloyd George Preview</h2>
                                    <DocumentUploadLloydGeorgePreview
                                        documents={documents
                                            .filter(
                                                (doc) => doc.docType === DOCUMENT_TYPE.LLOYD_GEORGE,
                                            )
                                            .sort((a, b) => a.position! - b.position!)}
                                    />
                                </>
                            )}
                    </>
                )}
                <div className="lloydgeorge_upload-submission mt-4">
                    <Button type="submit" id="form-submit" data-testid="form-submit-button">
                        Continue
                    </Button>
                    <LinkButton
                        type="button"
                        onClick={() => {
                            navigate(routeChildren.DOCUMENT_UPLOAD_REMOVE_ALL);
                        }}
                    >
                        Remove all
                    </LinkButton>
                </div>
            </form>
        </>
    );
};

export default DocumentSelectOrderStage;
