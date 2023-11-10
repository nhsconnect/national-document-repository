import React, { Dispatch, SetStateAction, useRef, useState } from 'react';
import { ReactComponent as Chevron } from '../../../styles/down-chevron.svg';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { useOnClickOutside } from 'usehooks-ts';
import { Card } from 'nhsuk-react-components';
import { Link } from 'react-router-dom';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import useRole from '../../../helpers/hooks/useRole';

export type Props = {
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

type PdfActionLink = {
    label: string;
    key: string;
    handler: () => void;
    unauthorised?: Array<REPOSITORY_ROLE>;
};
function LloydGeorgeRecordDetails({
    lastUpdated,
    numberOfFiles,
    totalFileSizeInByte,
    setStage,
}: Props) {
    const [showActionsMenu, setShowActionsMenu] = useState(false);
    const actionsRef = useRef(null);
    const role = useRole();
    const handleMoreActions = () => {
        setShowActionsMenu(!showActionsMenu);
    };
    useOnClickOutside(actionsRef, (e) => {
        setShowActionsMenu(false);
    });

    const actionLinks: Array<PdfActionLink> = [
        {
            label: 'See all files',
            key: 'see-all-files-link',
            handler: () => setStage(LG_RECORD_STAGE.SEE_ALL),
        },
        {
            label: 'Download all files',
            key: 'download-all-files-link',
            handler: () => setStage(LG_RECORD_STAGE.DOWNLOAD_ALL),
            unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        },
        {
            label: 'Delete all files',
            key: 'delete-all-files-link',
            handler: () => setStage(LG_RECORD_STAGE.DELETE_ALL),
            unauthorised: [REPOSITORY_ROLE.GP_CLINICAL],
        },
    ];

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
            <div className="lloydgeorge_record-details_actions">
                <div
                    data-testid="actions-menu"
                    className={`nhsuk-select lloydgeorge_record-details_actions-select ${
                        showActionsMenu ? 'lloydgeorge_record-details_actions-select--selected' : ''
                    }`}
                    onClick={handleMoreActions}
                >
                    <div
                        className={`lloydgeorge_record-details_actions-select_border ${
                            showActionsMenu
                                ? 'lloydgeorge_record-details_actions-select_border--selected'
                                : ''
                        }`}
                    />
                    <span className="lloydgeorge_record-details_actions-select_placeholder">
                        Select an action...
                    </span>
                    <Chevron className="lloydgeorge_record-details_actions-select_icon" />
                </div>
                {showActionsMenu && (
                    <div ref={actionsRef}>
                        <Card className="lloydgeorge_record-details_actions-menu">
                            <Card.Content>
                                <ol>
                                    {actionLinks.map((link) =>
                                        role && !link.unauthorised?.includes(role) ? (
                                            <li key={link.key} data-testid={link.key}>
                                                <Link
                                                    to="#"
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        link.handler();
                                                    }}
                                                >
                                                    {link.label}
                                                </Link>
                                            </li>
                                        ) : null,
                                    )}
                                </ol>
                            </Card.Content>
                        </Card>
                    </div>
                )}
            </div>
        </div>
    );
}

export default LloydGeorgeRecordDetails;
