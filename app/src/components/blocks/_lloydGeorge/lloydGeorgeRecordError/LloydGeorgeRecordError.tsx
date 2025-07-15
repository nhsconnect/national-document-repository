import React, { MouseEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import ServiceError from '../../../layout/serviceErrorBox/ServiceErrorBox';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import { routeChildren, routes } from '../../../../types/generic/routes';
import { ButtonLink } from 'nhsuk-react-components';
import useConfig from '../../../../helpers/hooks/useConfig';

type Props = {
    downloadStage: DOWNLOAD_STAGE;
};

function LloydGeorgeRecordError({ downloadStage }: Readonly<Props>) {
    const role = useRole();
    const navigate = useNavigate();
    const { featureFlags } = useConfig();

    const isAdmin = role === REPOSITORY_ROLE.GP_ADMIN;
    const uploadJourneyEnabled =
        featureFlags.uploadLloydGeorgeWorkflowEnabled && featureFlags.uploadLambdaEnabled;

    const renderTimeout = downloadStage === DOWNLOAD_STAGE.TIMEOUT;
    const renderUploadPath =
        downloadStage === DOWNLOAD_STAGE.NO_RECORDS && isAdmin && uploadJourneyEnabled;
    const renderNoRecords =
        downloadStage === DOWNLOAD_STAGE.NO_RECORDS && (!isAdmin || !uploadJourneyEnabled);
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
                <p>This patient does not have a Lloyd George record stored in this service.</p>

                <div className="lloydgeorge_record-stage_pdf-content-no_record">
                    <ButtonLink
                        className="lloydgeorge_record-stage_pdf-content-no_record-upload"
                        data-testid="upload-patient-record-button"
                        href="#"
                        onClick={(e: MouseEvent<HTMLAnchorElement>) => {
                            e.preventDefault();

                            navigate(routes.LLOYD_GEORGE_UPLOAD);
                            //navigate(routes.DOCUMENT_UPLOAD);
                        }}
                    >
                        Upload files for this patient
                    </ButtonLink>
                </div>
            </span>
        );
    } else if (renderNoRecords) {
        return <p>This patient does not have a Lloyd George record stored in this service.</p>;
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
