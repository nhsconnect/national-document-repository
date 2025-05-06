import { ButtonLink, Card } from 'nhsuk-react-components';
import { routes } from '../../../../types/generic/routes';
import ReducedPatientInfo from '../../../generic/reducedPatientInfo/ReducedPatientInfo';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import { useNavigate } from 'react-router';
import { useConfigContext } from '../../../../providers/configProvider/ConfigProvider';
import useTitle from '../../../../helpers/hooks/useTitle';

const DocumentUploadCompleteStage = () => {
    const navigate = useNavigate();
    const [config, setConfig] = useConfigContext();

    useTitle({ pageTitle: 'Record upload complete' });

    return (
        <div className="lloydgeorge_upload-complete" data-testid="upload-complete-page">
            <Card className="lloydgeorge_upload-complete_card" data-testid="upload-complete-card">
                <Card.Content className="lloydgeorge_upload-complete_card_content">
                    <Card.Heading
                        className="lloydgeorge_upload-complete_card_content_header"
                        headingLevel="h1"
                    >
                        Record&#40;s&#41; uploaded for
                    </Card.Heading>
                    <ReducedPatientInfo
                        className={'lloydgeorge_upload-complete_card_content_subheader'}
                    />
                    <div className="lloydgeorge_upload-complete_card_content_subheader">
                        Date uploaded: {getFormattedDate(new Date())}
                    </div>
                </Card.Content>
            </Card>

            <div>
                <p>
                    Your files have been successfully uploaded for this patient. If you have
                    uploaded Lloyd George records, they will now be combined into a single file.
                </p>
            </div>

            <ButtonLink
                role="button"
                data-testid="view-record-btn"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    setConfig({
                        ...config,
                        mockLocal: { ...config.mockLocal, recordUploaded: true },
                    });
                    navigate(routes.LLOYD_GEORGE);
                }}
            >
                View record
            </ButtonLink>

            <ButtonLink
                className="nhsuk-button nhsuk-button--secondary small-left-margin"
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
