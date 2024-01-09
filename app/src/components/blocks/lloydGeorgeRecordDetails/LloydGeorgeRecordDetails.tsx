import React, { Dispatch, SetStateAction, useRef, useState } from 'react';
import { ReactComponent as Chevron } from '../../../styles/down-chevron.svg';
import formatFileSize from '../../../helpers/utils/formatFileSize';
import { useOnClickOutside } from 'usehooks-ts';
import { Card, Button } from 'nhsuk-react-components';
import { Link } from 'react-router-dom';
import useRole from '../../../helpers/hooks/useRole';
import { actionLinks } from '../../../types/blocks/lloydGeorgeActions';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import { FieldValues, useForm, UseFormSetError, UseFormSetFocus } from 'react-hook-form';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';

export type Props = {
    lastUpdated: string;
    numberOfFiles: number;
    totalFileSizeInByte: number;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    userIsGpAdminNonBSOL?: boolean;
    setDownloadRemoveButtonClicked: Dispatch<SetStateAction<boolean>>;
    downloadRemoveButtonClicked: boolean;
    setError: UseFormSetError<FieldValues>;
    setFocus: UseFormSetFocus<FieldValues>;
};

function LloydGeorgeRecordDetails({
    lastUpdated,
    numberOfFiles,
    totalFileSizeInByte,
    setStage,
    userIsGpAdminNonBSOL,
    setDownloadRemoveButtonClicked,
    downloadRemoveButtonClicked,
    setError,
    setFocus,
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
            {userIsGpAdminNonBSOL ? (
                <div className="lloydgeorge_record-details_download-remove-button">
                    <Button
                        onClick={handleDownloadAndRemoveRecordButton}
                        className="lloydgeorge_record-details_download-remove-button-content"
                    >
                        Download and remove record
                    </Button>
                </div>
            ) : (
                role !== REPOSITORY_ROLE.GP_CLINICAL && (
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
                                                            to="#placeholder"
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
                )
            )}
        </div>
    );
}

export default LloydGeorgeRecordDetails;
