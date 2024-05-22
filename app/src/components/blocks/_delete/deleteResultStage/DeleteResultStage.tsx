import React, { Dispatch, MouseEvent, SetStateAction, useEffect } from 'react';
import { ButtonLink, Card } from 'nhsuk-react-components';
import { routes } from '../../../../types/generic/routes';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router';
import useRole from '../../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../../types/generic/authRole';
import { LG_RECORD_STAGE } from '../../../../types/blocks/lloydGeorgeStages';
import { DOWNLOAD_STAGE } from '../../../../types/generic/downloadStage';
import ReducedPatientInfo from '../../../generic/reducedPatientInfo/ReducedPatientInfo';
import { focusLayoutDiv } from '../../../../helpers/utils/manageFocus';
import useTitle from '../../../../helpers/hooks/useTitle';

export type Props = {
    numberOfFiles: number;
    setDownloadStage?: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function DeleteResultStage({ numberOfFiles, setStage, setDownloadStage }: Props) {
    const navigate = useNavigate();
    const role = useRole();

    // temp solution to focus on layout div so that skip-link can be selected.
    // we should remove this when this component become a separate route.
    useEffect(() => {
        focusLayoutDiv();
    }, []);

    const handleClick = (e: MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault();
        if (setStage && setDownloadStage) {
            setDownloadStage(DOWNLOAD_STAGE.REFRESH);
            setStage(LG_RECORD_STAGE.RECORD);
        }
        navigate(routes.LLOYD_GEORGE);
    };
    const isGP = role === REPOSITORY_ROLE.GP_ADMIN || role === REPOSITORY_ROLE.GP_CLINICAL;
    const pageHeader = 'You have permanently removed the record of:';
    useTitle({ pageTitle: pageHeader });
    return (
        <div className="deletion-complete">
            <Card className="deletion-complete_card">
                <Card.Content className="deletion-complete_card_content">
                    <Card.Heading
                        className="deletion-complete_card_content_header"
                        data-testid="deletion-complete_card_content_header"
                        headingLevel="h1"
                    >
                        {pageHeader}
                    </Card.Heading>
                    <ReducedPatientInfo className={'deletion-complete_card_content_subheader'} />
                </Card.Content>
            </Card>
            <p>You can no longer access this record using our storage.</p>
            <p className="lloydgeorge_delete-complete_paragraph-headers">What happens next</p>
            <ol>
                <li>
                    Make sure you safely store the paper version of this record, as it may be the
                    only copy
                </li>
                <li>
                    If you removed this record due to its retention period ending, you do not need
                    to store the paper copy
                </li>
                <li>
                    If you think you’ve made a mistake, you will need to upload this record again
                </li>
            </ol>
            <p className="lloydgeorge_delete-complete_paragraph-subheaders">
                Your responsibilities after removing this record
            </p>
            <p>
                Everyone in a health and care organisation is responsible for managing records
                appropriately. It is important all general practice staff understand their
                responsibilities for creating, and disposing of records appropriately.
            </p>
            <p className="lloydgeorge_delete-complete_paragraph-subheaders">
                Follow the Record Management Code of Practice
            </p>
            <p>
                The{' '}
                <a
                    href="https://transform.england.nhs.uk/information-governance/guidance/records-management-code"
                    target="_blank"
                    rel="noreferrer"
                >
                    Record Management Code of Practice
                </a>{' '}
                provides a framework for consistent and effective records management, based on
                established standards.
            </p>
            <p style={{ marginTop: 40 }}>
                {isGP ? (
                    <ButtonLink onClick={handleClick} data-testid="lg-return-btn" href="#">
                        Return to patient's Lloyd George record page
                    </ButtonLink>
                ) : (
                    <Link
                        id="start-again-link"
                        data-testid="start-again-link"
                        to=""
                        onClick={(e) => {
                            e.preventDefault();
                            navigate(routes.START);
                        }}
                    >
                        Start Again
                    </Link>
                )}
            </p>
        </div>
    );
}

export default DeleteResultStage;
