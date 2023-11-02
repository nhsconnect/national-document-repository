import React, { Dispatch, SetStateAction } from 'react';
import { ButtonLink, Card } from 'nhsuk-react-components';
import { PatientDetails } from '../../../types/generic/patientDetails';
import { LG_RECORD_STAGE } from '../../../pages/lloydGeorgeRecordPage/LloydGeorgeRecordPage';
import { USER_ROLE } from '../../../types/generic/roles';
import { routes } from '../../../types/generic/routes';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router';
import { formatNhsNumber } from '../../../helpers/utils/formatNhsNumber';

export type Props = {
    numberOfFiles: number;
    patientDetails: PatientDetails;
    setStage?: Dispatch<SetStateAction<LG_RECORD_STAGE>>;
    userType: USER_ROLE;
};

function DeletionConfirmationStage({ numberOfFiles, patientDetails, setStage, userType }: Props) {
    const navigate = useNavigate();
    const nhsNumber: string = patientDetails?.nhsNumber || '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);

    const handleClick = () => {
        if (setStage) {
            setStage(LG_RECORD_STAGE.RECORD);
        }
    };

    return (
        <div className="deletion-complete">
            <Card style={{ maxWidth: '620px' }} className="deletion-complete-card">
                <Card.Content>
                    <Card.Heading style={{ margin: 'auto' }}>Deletion complete</Card.Heading>
                    <Card.Description style={{ fontSize: '16px' }}>
                        {numberOfFiles} file{numberOfFiles !== 1 && 's'} from the{' '}
                        {userType === USER_ROLE.GP && 'Lloyd George '}
                        record of:{' '}
                    </Card.Description>
                    <Card.Description style={{ fontWeight: '700', fontSize: '24px' }}>
                        {patientDetails?.givenName?.map((name) => `${name} `)}
                        {patientDetails?.familyName}
                    </Card.Description>
                    <Card.Description style={{ fontSize: '16px' }}>
                        (NHS number: {formattedNhsNumber})
                    </Card.Description>
                </Card.Content>
            </Card>
            <p style={{ marginTop: 40 }}>
                {userType === USER_ROLE.GP ? (
                    <ButtonLink onClick={handleClick} data-testid="lg-return-btn">
                        Return to patient's Lloyd George record page
                    </ButtonLink>
                ) : (
                    <Link
                        id="start-again-link"
                        to=""
                        onClick={(e) => {
                            e.preventDefault();
                            navigate(routes.HOME);
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
