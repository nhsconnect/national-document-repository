import { Details, Table, WarningCallout } from 'nhsuk-react-components';
import React from 'react';
import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import formatFileSize from '../../../../helpers/utils/formatFileSize';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import ErrorBox from '../../../layout/errorBox/ErrorBox';
import useTitle from '../../../../helpers/hooks/useTitle';
import PatientSummary from '../../../generic/patientSummary/PatientSummary';

export interface Props {
    documents: Array<UploadDocument>;
}
const UploadSummary = ({ documents }: Props) => {
    const successfulUploads = documents.filter((document) => {
        return document.state === DOCUMENT_UPLOAD_STATE.SUCCEEDED;
    });

    const failedUploads = documents.filter((document) => {
        return [DOCUMENT_UPLOAD_STATE.FAILED, DOCUMENT_UPLOAD_STATE.INFECTED].includes(
            document.state,
        );
    });

    const tableMargin = { marginBottom: 50 };
    const tableCaption = (
        <>
            <h2 className="nhsuk-heading-m">
                {failedUploads.length} of {documents.length} files failed to upload
            </h2>
            <span className="nhsuk-error-message" id="example-error">
                <span className="nhsuk-u-visually-hidden">Error:</span> Documents that have failed
                to upload
            </span>
        </>
    );
    const pageHeader = 'Upload Summary';
    useTitle({ pageTitle: pageHeader });

    return (
        <section>
            {failedUploads.length > 0 && (
                <ErrorBox
                    errorBoxSummaryId={'failed-document-uploads-summary-title'}
                    errorInputLink={'#failed-uploads'}
                    messageTitle={'There is a problem'}
                    messageLinkBody={'Documents that have failed to upload'}
                    messageBody={
                        'Some documents failed to upload. You can try to upload the documents again if you wish, or they must be printed and sent via PCSE'
                    }
                ></ErrorBox>
            )}
            <h1 id="upload-summary-header">{pageHeader}</h1>
            {failedUploads.length > 0 && (
                <div className={'nhsuk-form-group--error margin'}>
                    <Table responsive caption={tableCaption} id="failed-uploads">
                        <Table.Body>
                            {failedUploads.map((document) => {
                                return (
                                    <Table.Row key={document.id}>
                                        <Table.Cell>{document.file.name}</Table.Cell>
                                        <Table.Cell>
                                            {formatFileSize(document.file.size)}
                                        </Table.Cell>
                                    </Table.Row>
                                );
                            })}
                        </Table.Body>
                    </Table>
                </div>
            )}
            {failedUploads.length === 0 && (
                <h2 id="upload-summary-confirmation">
                    All documents have been successfully uploaded on {getFormattedDate(new Date())}
                </h2>
            )}
            {successfulUploads.length > 0 && (
                <Details className="details-margin">
                    <Details.Summary
                        id="successful-uploads-dropdown"
                        aria-label="View successfully uploaded documents"
                    >
                        View successfully uploaded documents
                    </Details.Summary>
                    <Details.Text>
                        <Table
                            responsive
                            caption="Successfully uploaded documents"
                            captionProps={{
                                className: 'nhsuk-u-visually-hidden',
                            }}
                            id="successful-uploads"
                        >
                            <Table.Head>
                                <Table.Row>
                                    <Table.Cell>File Name</Table.Cell>
                                    <Table.Cell>File Size</Table.Cell>
                                </Table.Row>
                            </Table.Head>
                            <Table.Body>
                                {successfulUploads.map((document) => {
                                    return (
                                        <Table.Row key={document.id}>
                                            <Table.Cell>{document.file.name}</Table.Cell>
                                            <Table.Cell>
                                                {formatFileSize(document.file.size)}
                                            </Table.Cell>
                                        </Table.Row>
                                    );
                                })}
                            </Table.Body>
                        </Table>
                    </Details.Text>
                </Details>
            )}
            <PatientSummary />

            <WarningCallout className="upload-callout-warning" id="close-page-warning">
                <WarningCallout.Label>Before you close this page</WarningCallout.Label>
                <ul>
                    <li>
                        You could take a screenshot of this summary page and attach it to the
                        patient&apos;s record
                    </li>
                    <li>
                        When you have finished uploading, and the patient is deducted from your
                        practice, delete all temporary files created for upload on your computer
                    </li>
                    <li>
                        If you have accidentally uploaded incorrect documents, please contact
                        Primary Care Support England (PSCE)
                    </li>
                </ul>
            </WarningCallout>
        </section>
    );
};

export default UploadSummary;
