import { Card } from 'nhsuk-react-components';
import React, { Dispatch, HTMLAttributes, SetStateAction } from 'react';
import { LGRecordActionLink, RECORD_ACTION } from '../../../types/blocks/lloydGeorgeActions';
import { Link, useNavigate } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';

export type Props = HTMLAttributes<HTMLDivElement> & {
    recordLinks: Array<LGRecordActionLink>;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    showMenu: boolean;
    className?: string;
};

type SubSectionProps = {
    actionLinks: Array<LGRecordActionLink>;
    heading: string;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function RecordMenuCard({
    recordLinks,
    setStage,
    showMenu,
    className = 'lloydgeorge_record-stage_flex-row',
}: Props) {
    const updateActions = recordLinks.filter((link) => link.type === RECORD_ACTION.UPDATE);
    const downloadActions = recordLinks.filter((link) => link.type === RECORD_ACTION.DOWNLOAD);

    if (recordLinks.length === 0) {
        return <></>;
    }

    if (!showMenu) {
        return <></>;
    }
    return (
        <div className={className} data-testid="record-menu-card">
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
        </div>
    );
}

const SideMenuSubSection = ({ actionLinks, heading, setStage }: SubSectionProps) => {
    return (
        <>
            <h2 className="nhsuk-heading-m">{heading}</h2>
            <ol>
                {actionLinks.map((link) => (
                    <li key={link.key}>
                        <LinkItem link={link} setStage={setStage} />
                    </li>
                ))}
            </ol>
        </>
    );
};

type LinkItemProps = {
    link: LGRecordActionLink;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

const LinkItem = ({ link, setStage }: LinkItemProps) => {
    const navigate = useNavigate();

    if (link.href || link.stage) {
        return (
            <Link
                to="#placeholder"
                onClick={(e) => {
                    e.preventDefault();
                    if (link.href) navigate(link.href);
                    else if (link.stage) setStage(link.stage);
                }}
                data-testid={link.key}
            >
                {link.label}
            </Link>
        );
    } else {
        return (
            <button className="link-button" onClick={link.onClick} data-testid={link.key}>
                {link.label}
            </button>
        );
    }
};

export default RecordMenuCard;
