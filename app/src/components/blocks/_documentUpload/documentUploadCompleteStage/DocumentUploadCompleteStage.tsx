import { ButtonLink, Card } from 'nhsuk-react-components';
import { routes } from '../../../../types/generic/routes';
import { useNavigate } from 'react-router';
import useTitle from '../../../../helpers/hooks/useTitle';
import usePatient from '../../../../helpers/hooks/usePatient';

const DocumentUploadCompleteStage = () => {
    const navigate = useNavigate();
    const patientDetails = usePatient();

    useTitle({ pageTitle: 'Record upload complete' });

    return (
        <div className="lloydgeorge_upload-complete" data-testid="upload-complete-page">
            <Card className="lloydgeorge_upload-complete_card" data-testid="upload-complete-card">
                <Card.Content className="lloydgeorge_upload-complete_card_content">
                    <Card.Heading
                        className="lloydgeorge_upload-complete_card_content_header"
                        headingLevel="h1"
                    >
                        Upload complete
                    </Card.Heading>
                    <p className="mt-8">
                        You have successfully uploaded a digital Lloyd George record for:
                    </p>
                    <div className="lloydgeorge_upload-complete_card_content_subheader">
                        {patientDetails?.familyName}, {patientDetails?.givenName}
                    </div>
                    <p>NHS number: {patientDetails?.nhsNumber}</p>
                </Card.Content>
            </Card>

            <div>
                <p>
                    You can now view this patient's record within this service by searching using
                    their NHS number.
                </p>
            </div>

            <ButtonLink
                className="small-left-margin"
                data-testid="search-patient-btn"
                role="button"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    navigate(routes.SEARCH_PATIENT);
                }}
            >
                Search for a patient
            </ButtonLink>
        </div>
    );
};

export default DocumentUploadCompleteStage;
