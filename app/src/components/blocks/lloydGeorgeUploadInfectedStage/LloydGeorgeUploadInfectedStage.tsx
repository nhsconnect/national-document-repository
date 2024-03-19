import React from 'react';
import { ButtonLink, WarningCallout } from 'nhsuk-react-components';
import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../types/pages/UploadDocumentsPage/types';
import { useNavigate } from 'react-router';
import { routes } from '../../../types/generic/routes';

interface Props {
    documents: Array<UploadDocument>;
    restartUpload: () => void;
}

function LloydGeorgeUploadInfectedStage({ documents, restartUpload }: Props) {
    const navigate = useNavigate();

    const infectedUploads = documents.filter((document) => {
        return document.state === DOCUMENT_UPLOAD_STATE.INFECTED;
    });

    return (
        <div data-testid="failure-complete-page">
            <WarningCallout id="upload-stage-warning">
                <WarningCallout.Label>The record did not upload</WarningCallout.Label>
                <strong>Some of your files failed a virus scan:</strong>
                {infectedUploads.map((document) => (
                    <i key={document.id}>{document.file.name}</i>
                ))}{' '}
                <p>
                    This prevented the Lloyd George record being uploaded. You will need to check
                    your files and try again.
                </p>
                <p>
                    Make sure to safely store the full digital or paper Lloyd George record until
                    it's completely uploaded to this storage.
                </p>
                <p>
                    Contact the{' '}
                    <a
                        href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                        target="_blank"
                        rel="noreferrer"
                    >
                        NHS National Service Desk
                    </a>{' '}
                    if this issue continues.
                </p>{' '}
            </WarningCallout>

            <ButtonLink role="button" data-testid="retry-upload-btn" onClick={restartUpload}>
                Try upload again
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

export default LloydGeorgeUploadInfectedStage;
