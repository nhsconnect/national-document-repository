import React from 'react';
import useTitle from '../../../../helpers/hooks/useTitle';

const UploadConfirmationFailed = () => {
    const pageHeader = "We couldn't confirm the upload";
    useTitle({ pageTitle: pageHeader });

    return (
        <>
            <h1>{pageHeader}</h1>
            <p>
                The electronic health record was not uploaded for this patient. Please try uploading
                the record again in a few minutes.
            </p>
            <p>
                Make sure to safely store the electronic health record until it's completely
                uploaded to this storage.
            </p>
        </>
    );
};

export default UploadConfirmationFailed;
