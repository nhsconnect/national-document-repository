import { Card, Label } from 'nhsuk-react-components';
import React, { Dispatch, SetStateAction } from 'react';
import { PdfActionLink, RECORD_ACTION } from '../../../types/blocks/lloydGeorgeActions';
import useRole from '../../../helpers/hooks/useRole';
import { Link, useNavigate } from 'react-router-dom';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';

type Props = {
    recordLinks: Array<PdfActionLink>;
    setStage: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

type LinkProps = {
    actionLinks: Array<PdfActionLink>;
    heading: string;
};

function RecordMenuCard({ recordLinks, setStage }: Props) {
    const role = useRole();
    const navigate = useNavigate();

    const updateActions = recordLinks.filter((link) => link.type === RECORD_ACTION.UPDATE);
    const downloadActions = recordLinks.filter((link) => link.type === RECORD_ACTION.DOWNLOAD);

    const Links = ({ actionLinks, heading }: LinkProps) => (
        <>
            <Label bold={true} size={'m'}>
                {heading}
            </Label>
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

    return (
        <Card className="lloydgeorge_record-stage_menu">
            <Card.Content className="lloydgeorge_record-stage_menu-content">
                {updateActions.length > 0 && (
                    <Links actionLinks={updateActions} heading="Update record" />
                )}
                {downloadActions.length > 0 && (
                    <Links actionLinks={downloadActions} heading="Download record" />
                )}
            </Card.Content>
        </Card>
    );
}

export default RecordMenuCard;
