import React, { Dispatch, SetStateAction, useRef, useState } from 'react';
import { ReactComponent as Chevron } from '../../../styles/down-chevron.svg';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import { useOnClickOutside } from 'usehooks-ts';
import { Card, Button } from 'nhsuk-react-components';
import { Link } from 'react-router-dom';
import useRole from '../../../helpers/hooks/useRole';
import { actionLinks } from '../../../types/blocks/lloydGeorgeActions';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';

export type Props = {
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    userIsGpAdminNonBsol?: boolean;
};

function LloydGeorgeRecordDetails({
    lastUpdated,
    numberOfFiles,
    totalFileSizeInByte,
    setStage,
    userIsGpAdminNonBsol,
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
            {userIsGpAdminNonBsol ? (
                <Button className="lloydgeorge_record-details_download-remove-button">
                    Download and remove record
                </Button>
            ) : (
                <div className="lloydgeorge_record-details_actions">
                    <div
                        data-testid="actions-menu"
                        className={`nhsuk-select lloydgeorge_record-details_actions-select ${
                            showActionsMenu
                                ? 'lloydgeorge_record-details_actions-select--selected'
                                : ''
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
                                                            setStage(link.stage);
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
            )}
        </div>
    );
}

export default LloydGeorgeRecordDetails;
