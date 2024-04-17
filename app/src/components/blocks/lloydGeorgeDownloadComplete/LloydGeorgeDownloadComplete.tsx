import React, { Dispatch, SetStateAction, useEffect } from 'react';
import { Button, Card } from 'nhsuk-react-components';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import ReducedPatientInfo from '../../generic/reducedPatientInfo/ReducedPatientInfo';
import { focusLayoutDiv } from '../../../helpers/utils/manageFocus';
import pageTitle from '../../layout/pageTitle/PageTitle';

export type Props = {
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    setDownloadStage: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
    deleteAfterDownload: boolean;
};

function LloydGeorgeDownloadComplete({ setStage, setDownloadStage, deleteAfterDownload }: Props) {
    // temp solution to focus on layout div so that skip-link can be selected.
    // we should remove this when this component become a separate route.
    useEffect(() => {
        focusLayoutDiv();
    }, []);

    const handleReturnButtonClick = () => {
        setStage(LG_RECORD_STAGE.RECORD);
        if (deleteAfterDownload) {
            setDownloadStage(DOWNLOAD_STAGE.REFRESH);
        }
    };
    const pageHeader = 'Download complete';
    pageTitle({ pageTitle: pageHeader });
    return (
        <div className="lloydgeorge_download-complete">
            <Card className="lloydgeorge_download-complete_details">
                <Card.Content className="lloydgeorge_download-complete_details-content">
                    <Card.Heading
                        className="lloydgeorge_download-complete_details-content_header"
                        headingLevel="h1"
                    >
                        {pageHeader}
                    </Card.Heading>
                    <Card.Description className="lloydgeorge_download-complete_details-content_description">
                        You have successfully downloaded the{'\n'}
                        Lloyd George record of:
                    </Card.Description>
                    <ReducedPatientInfo
                        className={'lloydgeorge_download-complete_details-content_subheader'}
                    />
                </Card.Content>
            </Card>
            {deleteAfterDownload ? (
                <>
                    <p>This record has been removed from our storage.</p>
                    <p className="lloydgeorge_download-complete_paragraph-headers">
                        Keep this patient's record safe
                    </p>
                    <ol>
                        <li>
                            Store the record in an accessible and recoverable format within a secure
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
                    <p className="lloydgeorge_download-complete_paragraph-headers">
                        Your responsibilities with this record
                    </p>
                    <p>
                        Everyone in a health and care organisation is responsible for managing
                        records appropriately. It is important all general practice staff understand
                        their responsibilities for creating, maintaining, and disposing of records
                        appropriately.
                    </p>
                    <p className="lloydgeorge_download-complete_paragraph-headers">
                        Follow the Record Management Code of Practice
                    </p>
                    <p>
                        The{' '}
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
