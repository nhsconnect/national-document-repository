import React, { Dispatch, SetStateAction } from 'react';
import { Link } from 'react-router-dom';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import ServiceError from '../../layout/serviceErrorBox/ServiceErrorBox';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';

type Props = {
    downloadStage: DOWNLOAD_STAGE;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function LloydGeorgeRecordError({ downloadStage, setStage }: Props) {
    if (downloadStage === DOWNLOAD_STAGE.TIMEOUT) {
        return (
            <span>
                {'The Lloyd George document is too large to view in a browser, '}
                <Link
                    to="#"
                    data-testid="download-instead-link"
                    onClick={(e) => {
                        e.preventDefault();
                        setStage(LG_RECORD_STAGE.DOWNLOAD_ALL);
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
