import React, { MouseEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import ServiceError from '../../../layout/serviceErrorBox/ServiceErrorBox';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import { routeChildren, routes } from '../../../../types/generic/routes';
import useIsBSOL from '../../../../helpers/hooks/useIsBSOL';
import { ButtonLink } from 'nhsuk-react-components';
import useConfig from '../../../../helpers/hooks/useConfig';

type Props = {
    downloadStage: DOWNLOAD_STAGE;
};

function LloydGeorgeRecordError({ downloadStage }: Props) {
    const role = useRole();
    const navigate = useNavigate();
    const isBSOL = useIsBSOL();
    const { featureFlags } = useConfig();

    const isAdminBsol = role === REPOSITORY_ROLE.GP_ADMIN && isBSOL;
    const uploadJourneyEnabled =
        featureFlags.uploadLloydGeorgeWorkflowEnabled && featureFlags.uploadLambdaEnabled;

    const renderTimeout = downloadStage === DOWNLOAD_STAGE.TIMEOUT;
    const renderUploadPath =
        downloadStage === DOWNLOAD_STAGE.NO_RECORDS && isAdminBsol && uploadJourneyEnabled;
    const renderNoRecords =
        downloadStage === DOWNLOAD_STAGE.NO_RECORDS && (!isAdminBsol || !uploadJourneyEnabled);
    const renderUploadInProgress = downloadStage === DOWNLOAD_STAGE.UPLOADING;

    if (renderTimeout) {
        return (
            <span>
                <p data-testid="lloyd-george-record-error-message">
                    {'The Lloyd George document is too large to view in a browser, '}
                    <Link
                        to="#"
                        data-testid="download-instead-link"
                        onClick={(e) => {
                            e.preventDefault();
                            role === REPOSITORY_ROLE.GP_CLINICAL
                                ? navigate(routes.UNAUTHORISED)
                                : navigate(routeChildren.LLOYD_GEORGE_DOWNLOAD);
                        }}
                    >
                        please download instead
                    </Link>
                    {'.'}
                </p>
            </span>
        );
    } else if (renderUploadPath) {
        return (
            <span>
                <h3 data-testid="no-records-title">No records available for this patient.</h3>
                <p data-testid="upload-patient-record-text">
                    You can upload full or part of a patient record. You can upload supporting files
                    once the record is uploaded.
                </p>

                <div className="lloydgeorge_record-stage_pdf-content-no_record">
                    <ButtonLink
                        className="lloydgeorge_record-stage_pdf-content-no_record-upload"
                        data-testid="upload-patient-record-button"
                        href="#"
                        onClick={(e: MouseEvent<HTMLAnchorElement>) => {
                            e.preventDefault();
                            navigate(routes.LLOYD_GEORGE_UPLOAD);
                        }}
                    >
                        Upload patient record
                    </ButtonLink>
                </div>
            </span>
        );
    } else if (renderNoRecords) {
        return <p>No documents are available.</p>;
    } else if (renderUploadInProgress) {
        return (
            <p>
                You can view this record once it’s finished uploading. This may take a few minutes.
            </p>
        );
    }
    return <ServiceError message="An error has occurred when creating the Lloyd George preview." />;
}

export default LloydGeorgeRecordError;
