import React, { useState } from 'react';
import { ButtonLink, Card, Details } from 'nhsuk-react-components';
import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import usePatient from '../../../helpers/hooks/usePatient';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import { useNavigate } from 'react-router';
import { routes } from '../../../types/generic/routes';
interface Props {
    documents: Array<UploadDocument>;
}

function LloydGeorgeUploadComplete({ documents }: Props) {
    const navigate = useNavigate();
    const patientDetails = usePatient();
    const [isExpanded, setIsExpanded] = useState(true);

    const nhsNumber: string = patientDetails?.nhsNumber || '';
    // const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const formattedNhsNumber = '123 456 0000';

    const successfulUploads = documents.filter((document) => {
        return document.state === DOCUMENT_UPLOAD_STATE.SUCCEEDED;
    });

    return (
        <div className="lg-upload-complete" style={{ maxWidth: '620px' }}>
            <Card className="lg-upload-complete-card">
                <Card.Content>
                    <Card.Heading style={{ margin: 'auto' }}>Record uploaded for</Card.Heading>
                    <Card.Description style={{ fontWeight: '600', fontSize: '16px' }}>
                        Test Patient Name
                        {/*{patientDetails?.givenName?.map((name) => `${name} `)}*/}
                        {/*{patientDetails?.familyName}*/}
                    </Card.Description>
                    <Card.Description style={{ fontSize: '16px' }}>
                        NHS number: {formattedNhsNumber}
                    </Card.Description>
                    <Card.Description style={{ fontWeight: '600', fontSize: '16px' }}>
                        Date uploaded: {getFormattedDate(new Date())}
                    </Card.Description>
                </Card.Content>
            </Card>
            <h5>
                You have successfully uploaded {successfulUploads.length} file
                {successfulUploads.length !== 1 && 's'}
            </h5>
            {successfulUploads.length > 0 && (
                <>
                    <Details open>
                        <Details.Summary
                            id="successful-lg-uploads-dropdown"
                            aria-label="View successfully uploaded documents"
                            onClick={() => setIsExpanded(!isExpanded)}
                        >
                            {isExpanded ? 'Hide files' : 'View files'}
                        </Details.Summary>
                        <Details.Text className="successful-lg-uploads-list">
                            {successfulUploads.map((document) => {
                                return <p key={document.id}>{document.file.name}</p>;
                            })}
                        </Details.Text>
                    </Details>
                </>
            )}
            <h5>What happens next</h5>
            <p>
                You have successfully created a Lloyd George record for this patient. The uploaded
                files will be combined to make up the Lloyd George record.
            </p>
            <p>
                You can upload more files to their record if needed, but you cannot upload duplicate
                files with the same name as previous uploads.
            </p>
            <p>If you need to replace a file, you will need to remove it and re-upload it again.</p>

            <ButtonLink
                role="button"
                data-testid="view-record-btn"
                onClick={() => {
                    navigate(routes.LLOYD_GEORGE);
                }}
            >
                View record
            </ButtonLink>

            <ButtonLink
                className="nhsuk-button nhsuk-button--secondary"
                data-testid="search-patient-btn"
                style={{ marginLeft: 18 }}
                role="button"
                onClick={() => {
                    navigate(routes.SEARCH_PATIENT);
                }}
            >
                Search for a patient
            </ButtonLink>
        </div>
    );
}

export default LloydGeorgeUploadComplete;
