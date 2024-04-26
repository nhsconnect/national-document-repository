import { Card } from 'nhsuk-react-components';
import React, { Dispatch, SetStateAction } from 'react';
import { PdfActionLink, RECORD_ACTION } from '../../../types/blocks/lloydGeorgeActions';
import { Link, useNavigate } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';

type Props = {
    recordLinks: Array<PdfActionLink>;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

type SubSectionProps = {
    actionLinks: Array<PdfActionLink>;
    heading: string;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function RecordMenuCard({ recordLinks, setStage }: Props) {
    const updateActions = recordLinks.filter((link) => link.type === RECORD_ACTION.UPDATE);
    const downloadActions = recordLinks.filter((link) => link.type === RECORD_ACTION.DOWNLOAD);

    return (
        <Card className="lloydgeorge_record-stage_menu">
            <Card.Content className="lloydgeorge_record-stage_menu-content">
                {updateActions.length > 0 && (
                    <SideMenuSubSection
                        actionLinks={updateActions}
                        heading="Update record"
                        setStage={setStage}
                    />
                )}
                {downloadActions.length > 0 && (
                    <SideMenuSubSection
                        actionLinks={downloadActions}
                        heading="Download record"
                        setStage={setStage}
                    />
                )}
            </Card.Content>
        </Card>
    );
}

const SideMenuSubSection = ({ actionLinks, heading, setStage }: SubSectionProps) => {
    const navigate = useNavigate();
    return (
        <>
            <h2 className="nhsuk-heading-m">{heading}</h2>
            <ol>
                {actionLinks.map((link) => (
                    <li key={link.key} data-testid={link.key}>
                        <Link
                            to="#placeholder"
                            onClick={(e) => {
                                e.preventDefault();
                                if (link.href) navigate(link.href);
                                else if (link.stage) setStage(link.stage);
                            }}
                        >
                            {link.label}
                        </Link>
                    </li>
                ))}
            </ol>
        </>
    );
};
export default RecordMenuCard;
