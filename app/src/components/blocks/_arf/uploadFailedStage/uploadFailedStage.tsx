import React from 'react';
import useTitle from '../../../../helpers/hooks/useTitle';

const UploadFailedStage = () => {
    const pageHeader = 'All files failed to upload';
    useTitle({ pageTitle: pageHeader });

    return (
        <>
            <h1>{pageHeader}</h1>
            <p>
                The electronic health record was not uploaded for this patient. You will need to
                check your files and try again.
            </p>
            <p>
                Make sure to safely store the electronic health record until it's completely
                uploaded to this storage.
            </p>
        </>
    );
};

export default UploadFailedStage;
