import React, { Dispatch, SetStateAction } from 'react';
import { ButtonLink, Card } from 'nhsuk-react-components';
import { routes } from '../../../types/generic/routes';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router';
import useRole from '../../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../../types/generic/authRole';
import { LG_RECORD_STAGE } from '../../../types/blocks/lloydGeorgeStages';
import { DOWNLOAD_STAGE } from '../../../types/generic/downloadStage';
import ReducedPatientInfo from '../../generic/reducedPatientInfo/ReducedPatientInfo';

export type Props = {
    numberOfFiles: number;
    setDownloadStage?: Dispatch<SetStateAction<DOWNLOAD_STAGE>>;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
};

function DeletionConfirmationStage({ numberOfFiles, setStage, setDownloadStage }: Props) {
    const navigate = useNavigate();
    const role = useRole();
    const handleClick = () => {
        if (setStage && setDownloadStage) {
            setDownloadStage(DOWNLOAD_STAGE.REFRESH);
            setStage(LG_RECORD_STAGE.RECORD);
        }
    };
    const isGP = role === REPOSITORY_ROLE.GP_ADMIN || role === REPOSITORY_ROLE.GP_CLINICAL;
    return (
        <div className="deletion-complete">
            <Card className="deletion-complete_card">
                <Card.Content className="deletion-complete_card_content">
                    <Card.Heading className="deletion-complete_card_content_header">
                        Deletion complete
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
                    <ButtonLink onClick={handleClick} data-testid="lg-return-btn">
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
