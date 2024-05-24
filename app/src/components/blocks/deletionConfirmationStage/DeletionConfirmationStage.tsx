import React, { Dispatch, MouseEvent, SetStateAction, useEffect } from 'react';
import { ButtonLink, Card } from 'nhsuk-react-components';
import { routes } from '../../../types/generic/routes';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import ReducedPatientInfo from '../../generic/reducedPatientInfo/ReducedPatientInfo';
import { focusLayoutDiv } from '../../../helpers/utils/manageFocus';
import useTitle from '../../../helpers/hooks/useTitle';

export type Props = {
    numberOfFiles: number;
    setDownloadStage?: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function DeletionConfirmationStage({ numberOfFiles, setStage, setDownloadStage }: Props) {
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

            if (isGP) {
                navigate(routes.LLOYD_GEORGE);
            } else {
                navigate(routes.START);
            }
        }
    };

    const isGP = role === REPOSITORY_ROLE.GP_ADMIN || role === REPOSITORY_ROLE.GP_CLINICAL;
    const pageHeader = 'Deletion complete';
    useTitle({ pageTitle: pageHeader });
    return (
        <div className="deletion-complete">
            <Card className="deletion-complete_card">
                <Card.Content className="deletion-complete_card_content">
                    <Card.Heading
                        className="deletion-complete_card_content_header"
                        headingLevel="h1"
                    >
                        {pageHeader}
                    </Card.Heading>
                    <Card.Description className="deletion-complete_card_content_description">
                        You have successfully deleted {numberOfFiles} file(s){'\n'}
                        from the {isGP && 'Lloyd George '}
                        record of:{' '}
                    </Card.Description>
                    <ReducedPatientInfo className={'deletion-complete_card_content_subheader'} />
                </Card.Content>
            </Card>
            <p style={{ marginTop: 40 }}>
                {isGP ? (
                    <ButtonLink onClick={handleClick} data-testid="lg-return-btn" href="#">
                        Return to patient's Lloyd George record page
                    </ButtonLink>
                ) : (
                    <Link
                        id="start-again-link"
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

export default DeletionConfirmationStage;
