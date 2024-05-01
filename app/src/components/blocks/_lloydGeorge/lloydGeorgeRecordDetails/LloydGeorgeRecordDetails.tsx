import React from 'react';
import formatFileSize from '../../../../helpers/utils/formatFileSize';

export type Props = {
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
};

function LloydGeorgeRecordDetails({ lastUpdated, numberOfFiles, totalFileSizeInByte }: Props) {
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
        </div>
    );
}

export default LloydGeorgeRecordDetails;
