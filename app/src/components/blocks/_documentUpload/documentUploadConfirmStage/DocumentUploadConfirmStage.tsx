import { Button, Table } from 'nhsuk-react-components';
import useTitle from '../../../../helpers/hooks/useTitle';
import { DOCUMENT_TYPE, UploadDocument } from '../../../../types/pages/UploadDocumentsPage/types';
import PatientSimpleSummary from '../../../generic/patientSimpleSummary/PatientSimpleSummary';
import BackButton from '../../../generic/backButton/BackButton';
import { useNavigate } from 'react-router';
import { routes } from '../../../../types/generic/routes';
import { useState } from 'react';
import Pagination from '../../../generic/pagination/Pagination';

type Props = {
    documents: UploadDocument[];
    startUpload: () => Promise<void>;
};

const DocumentUploadConfirmStage = ({ documents, startUpload }: Props) => {
    const [currentPage, setCurrentPage] = useState<number>(0);
    const navigate = useNavigate();
    const pageSize = 10;

    const pageTitle = 'Check your files before uploading';
    useTitle({ pageTitle });

    const currentItems = () => {
        const skipCount = currentPage * pageSize;
        return documents.slice(skipCount, skipCount + pageSize);
    };

    const totalPages = (): number => {
        return Math.ceil(documents.length / pageSize);
    };

    return (
        <div className="document-upload-confirm">
            <BackButton />
            <h1>{pageTitle}</h1>
            <p>
                Files will be combined into a single PDF document to create a digital Lloyd George
                record for:
            </p>
            <PatientSimpleSummary />

            <div style={{ borderBottom: '1px solid black' }}>
                <h4 style={{ width: '100%', display: 'flex', justifyContent: 'space-between' }}>
                    <span>Files to be uploaded</span>
                    <button
                        className="govuk-link"
                        rel="change"
                        onClick={(e) => {
                            e.preventDefault();
                            navigate(routes.DOCUMENT_UPLOAD);
                        }}
                    >
                        <strong style={{ textDecoration: 'underline', cursor: 'pointer' }}>
                            Change
                        </strong>
                    </button>
                </h4>
            </div>

            <Table id="selected-documents-table">
                <Table.Head>
                    <Table.Row>
                        <Table.Cell width="80%">Filename</Table.Cell>
                        <Table.Cell style={{ whiteSpace: 'pre', wordBreak: 'keep-all' }}>
                            Position
                        </Table.Cell>
                    </Table.Row>
                </Table.Head>

                <Table.Body>
                    {currentItems().map((document: UploadDocument) => {
                        return (
                            <Table.Row key={document.id} id={document.file.name}>
                                <Table.Cell>
                                    <div>{document.file.name}</div>
                                </Table.Cell>
                                <Table.Cell>
                                    <div>
                                        {document.docType === DOCUMENT_TYPE.LLOYD_GEORGE
                                            ? document.position
                                            : 'N/A'}
                                    </div>
                                </Table.Cell>
                            </Table.Row>
                        );
                    })}
                </Table.Body>
            </Table>

            <Pagination
                totalPages={totalPages()}
                currentPage={currentPage}
                setCurrentPage={setCurrentPage}
            />

            <Button onClick={startUpload}>Upload files</Button>
        </div>
    );
};

export default DocumentUploadConfirmStage;
