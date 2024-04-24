import React, { useEffect } from 'react';
import { ButtonLink, WarningCallout } from 'nhsuk-react-components';
import {
    DOCUMENT_UPLOAD_STATE,
    UploadDocument,
} from '../../../../types/pages/UploadDocumentsPage/types';
import { useNavigate } from 'react-router';
import { routes } from '../../../../types/generic/routes';
import { focusLayoutDiv } from '../../../../helpers/utils/manageFocus';
import ServiceDeskLink from '../../../generic/serviceDeskLink/ServiceDeskLink';
import useTitle from '../../../../helpers/hooks/useTitle';

interface Props {
    documents: Array<UploadDocument>;
    restartUpload: () => void;
}

function LloydGeorgeUploadInfectedStage({ documents, restartUpload }: Props) {
    const navigate = useNavigate();

    // temp solution to focus on layout div so that skip-link can be selected.
    // we should remove this if this component become a separate route.
    useEffect(() => {
        focusLayoutDiv();
    }, []);

    const infectedUploads = documents.filter((document) => {
        return document.state === DOCUMENT_UPLOAD_STATE.INFECTED;
    });
    const pageHeader = 'The record did not upload';
    useTitle({ pageTitle: pageHeader });
    return (
        <div data-testid="failure-complete-page">
            <WarningCallout id="upload-stage-warning">
                <WarningCallout.Label headingLevel="h1">{pageHeader}</WarningCallout.Label>
                <p>
                    <strong>Some of your files failed a virus scan:</strong>
                </p>
                <ul style={{ listStyle: 'none' }}>
                    {infectedUploads.map((document) => (
                        <li key={document.id}>
                            <i key={document.id}>{document.file.name}</i>
                        </li>
                    ))}{' '}
                </ul>
                <p>
                    This prevented the Lloyd George record being uploaded. You will need to check
                    your files and try again.
                </p>
                <p>
                    Make sure to safely store the full digital or paper Lloyd George record until
                    it's completely uploaded to this storage.
                </p>
                <p>
                    Contact the <ServiceDeskLink /> if this issue continues.
                </p>{' '}
            </WarningCallout>

            <ButtonLink
                role="button"
                data-testid="retry-upload-btn"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    restartUpload();
                }}
            >
                Try upload again
            </ButtonLink>

            <ButtonLink
                className="nhsuk-button nhsuk-button--secondary"
                data-testid="search-patient-btn"
                style={{ marginLeft: 18 }}
                role="button"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    navigate(routes.SEARCH_PATIENT);
                }}
            >
                Search for a patient
            </ButtonLink>
        </div>
    );
}

export default LloydGeorgeUploadInfectedStage;
