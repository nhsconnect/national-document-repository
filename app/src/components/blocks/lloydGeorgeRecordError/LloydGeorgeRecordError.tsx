import React, { Dispatch, SetStateAction } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import ServiceError from '../../layout/serviceErrorBox/ServiceErrorBox';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { routes } from '../../../types/generic/routes';

type Props = {
    downloadStage: DOWNLOAD_STAGE;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function LloydGeorgeRecordError({ downloadStage, setStage }: Props) {
    const role = useRole();
    const navigate = useNavigate();

    if (downloadStage === DOWNLOAD_STAGE.TIMEOUT) {
        return (
            <span>
                <p data-testid="llyoyd-george-record-error-message">
                    {'The Lloyd George document is too large to view in a browser, '}
                </p>
                <Link
                    to="#"
                    data-testid="download-instead-link"
                    onClick={(e) => {
                        e.preventDefault();
                        if (role === REPOSITORY_ROLE.GP_CLINICAL) {
                            navigate(routes.UNAUTHORISED);
                        } else {
                            setStage(LG_RECORD_STAGE.DOWNLOAD_ALL);
                        }
                    }}
                >
                    please download instead
                </Link>
                {'.'}
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
