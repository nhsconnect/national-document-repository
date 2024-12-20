import React from 'react';

export type Props = {
    lastUpdated: string;
};

function LloydGeorgeRecordDetails({ lastUpdated }: Props) {
    return (
        <div className="lloydgeorge_record-details">
            <div className="lloydgeorge_record-details_details">
                <div className="lloydgeorge_record-details_details--last-updated">
                    Last updated: {lastUpdated}
                </div>
            </div>
        </div>
    );
}

export default LloydGeorgeRecordDetails;
