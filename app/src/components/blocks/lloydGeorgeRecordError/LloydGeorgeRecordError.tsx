import React, { Dispatch, SetStateAction } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import ServiceError from '../../layout/serviceErrorBox/ServiceErrorBox';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { routes } from '../../../types/generic/routes';
import useIsBSOL from '../../../helpers/hooks/useIsBSOL';
import { ButtonLink } from 'nhsuk-react-components';

type Props = {
    downloadStage: DOWNLOAD_STAGE;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function LloydGeorgeRecordError({ downloadStage, setStage }: Props) {
    const role = useRole();
    const navigate = useNavigate();
    const isBSOL = useIsBSOL();

    if (downloadStage === DOWNLOAD_STAGE.TIMEOUT) {
        return (
            <span>
                <p data-testid="llyoyd-george-record-error-message">
                    {'The Lloyd George document is too large to view in a browser, '}
                    <Link
                        to="#"
                        data-testid="download-instead-link"
                        onClick={(e) => {
                            e.preventDefault();
                            role === REPOSITORY_ROLE.GP_CLINICAL
                                ? navigate(routes.UNAUTHORISED)
                                : setStage(LG_RECORD_STAGE.DOWNLOAD_ALL);
                        }}
                    >
                        please download instead
                    </Link>
                    {'.'}
                </p>
            </span>
        );
    } else if (
        downloadStage === DOWNLOAD_STAGE.NO_RECORDS &&
        role === REPOSITORY_ROLE.GP_ADMIN &&
        isBSOL
    ) {
        return (
            <span>
                <h3>No records available for this patient</h3>
                <p>
                    You can upload full or part of a patient record. You can upload supporting files
                    once the record is uploaded.
                </p>
                <div className="lloydgeorge_record-stage_header-content-no_record">
                    <ButtonLink
                        className="lloydgeorge_record-stage_header-content-no_record-upload"
                        onClick={() => {
                            navigate(routes.LLOYD_GEORGE_UPLOAD);
                        }}
                    >
                        Upload patient record
                    </ButtonLink>
                </div>
            </span>
        );
    } else if (downloadStage === DOWNLOAD_STAGE.NO_RECORDS) {
        return <span>No documents are available.</span>;
    } else {
        return (
            <ServiceError message="An error has occurred when creating the Lloyd George preview." />
        );
    }
}

export default LloydGeorgeRecordError;
