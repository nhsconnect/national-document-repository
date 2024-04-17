import React, { Dispatch, SetStateAction } from 'react';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import { Button } from 'nhsuk-react-components';
import useRole from '../../../helpers/hooks/useRole';
import { FieldValues, UseFormSetError, UseFormSetFocus } from 'react-hook-form';
import useIsBSOL from '../../../helpers/hooks/useIsBSOL';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';

export type Props = {
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    setDownloadRemoveButtonClicked: Dispatch<SetStateAction<boolean>>;
    downloadRemoveButtonClicked: boolean;
    setError: UseFormSetError<FieldValues>;
    setFocus: UseFormSetFocus<FieldValues>;
};

function LloydGeorgeRecordDetails({
    lastUpdated,
    numberOfFiles,
    totalFileSizeInByte,
    setDownloadRemoveButtonClicked,
    downloadRemoveButtonClicked,
    setError,
    setFocus,
}: Props) {
    const role = useRole();
    const isBSOL = useIsBSOL();
    const userIsGpAdminNonBSOL = role === REPOSITORY_ROLE.GP_ADMIN && !isBSOL;

    const handleDownloadAndRemoveRecordButton = () => {
        if (downloadRemoveButtonClicked) {
            setError('confirmDownloadRemove', { type: 'custom', message: 'true' });
        }
        setFocus('confirmDownloadRemove');
        setDownloadRemoveButtonClicked(true);
    };

    return (
        <div className="lloydgeorge_record-details">
            <div className="lloydgeorge_record-details_details">
                <div className="lloydgeorge_record-details_details--last-updated">
                    Last updated: {lastUpdated}
                </div>
                <div className="lloydgeorge_record-details_details--num-files">
                    <span>{numberOfFiles} files</span>
                    {' | '}
                    <span>File size: {formatFileSize(totalFileSizeInByte)}</span>
                    {' | '}
                    <span>File format: PDF</span>
                    {' |'}
                </div>
            </div>
            {userIsGpAdminNonBSOL && (
                <div className="lloydgeorge_record-details_download-remove-button">
                    <Button
                        data-testid="download-and-remove-record-btn"
                        onClick={handleDownloadAndRemoveRecordButton}
                        className="lloydgeorge_record-details_download-remove-button-content"
                    >
                        Download and remove record
                    </Button>
                </div>
            )}
        </div>
    );
}

export default LloydGeorgeRecordDetails;
