import React, { Dispatch, SetStateAction } from 'react';
import { Button, Card } from 'nhsuk-react-components';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import usePatient from '../../../helpers/hooks/usePatient';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';

export type Props = {
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    setDownloadStage: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
    deleteAfterDownload: boolean;
};

function LloydGeorgeDownloadComplete({ setStage, setDownloadStage, deleteAfterDownload }: Props) {
    const patientDetails = usePatient();

    const handleReturnButtonClick = () => {
        setStage(LG_RECORD_STAGE.RECORD);
        if (deleteAfterDownload) {
            setDownloadStage(DOWNLOAD_STAGE.REFRESH);
        }
    };

    return (
        <div className="lloydgeorge_download-complete">
            <Card className="lloydgeorge_download-complete_details">
                <Card.Content className="lloydgeorge_download-complete_details-content">
                    <Card.Heading className="lloydgeorge_download-complete_details-content_header">
                        Download complete
                    </Card.Heading>
                    Documents from the Lloyd George record of:
                    <div className="lloydgeorge_download-complete_details-content_subheader">
                        <strong>
                            {patientDetails?.givenName + ' ' + patientDetails?.familyName}
                        </strong>
                    </div>
                    <div>{`(NHS number: ${patientDetails?.nhsNumber})`}</div>
                </Card.Content>
            </Card>
            {deleteAfterDownload ? (
                <>
                    <p>This record has been removed from our storage.</p>
                    <h2>Keep this patient's record safe</h2>
                    <ol>
                        <li>
                            Store the record in accessible and recoverable format within a secure
                            network folder
                        </li>
                        <li>
                            Ensure all access to the record is auditable, so information can be
                            provided about who accessed the record
                        </li>
                        <li>
                            If the patient moves practice, you must make sure the patient record
                            safely transfers to their new practice
                        </li>
                        <li>
                            Follow data protection principles outlined in{' '}
                            <a href="https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/">
                                UK General Data Protection Regulation (UK GDPR)
                            </a>
                        </li>
                    </ol>
                    <h3>Your responsibilities with this record</h3>
                    <p>
                        Everyone in a health and care organisation is responsible for managing
                        records appropriately. It is important all general practice staff understand
                        their responsibilities for creating, maintaining, and disposing of records
                        appropriately.
                    </p>
                    <h3>Follow the Record Management Code of Practice</h3>
                    <p>
                        <a href="https://transform.england.nhs.uk/information-governance/guidance/records-management-code">
                            Record Management Code of Practice
                        </a>{' '}
                        provides a framework for consistent and effective records management, based
                        on established standards.
                    </p>
                </>
            ) : (
                <Button onClick={handleReturnButtonClick} data-testid="return-btn">
                    Return to patient's available medical records
                </Button>
            )}
        </div>
    );
}

export default LloydGeorgeDownloadComplete;
