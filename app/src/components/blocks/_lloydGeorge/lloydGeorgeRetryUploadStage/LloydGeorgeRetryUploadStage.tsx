import { Button, ButtonLink, WarningCallout } from 'nhsuk-react-components';
import { useNavigate } from 'react-router-dom';
import { routes } from '../../../../types/generic/routes';
import ServiceDeskLink from '../../../generic/serviceDeskLink/ServiceDeskLink';

function LloydGeorgeRetryUploadStage() {
    const navigate = useNavigate();
    return (
        <>
            <WarningCallout>
                <WarningCallout.Label headingLevel="h2">
                    The record did not upload
                </WarningCallout.Label>
                <p>
                    <strong>
                        One or more files failed to upload, which prevented the full record being
                        uploaded
                    </strong>
                </p>
                <p>
                    The Lloyd George record was not uploaded for this patient. You will need to
                    check your files and try again.
                </p>
                <p>
                    Make sure to safely store the full digital or paper Lloyd George record until
                    it's completely uploaded to this storage.
                </p>
                <p>
                    Contact the <ServiceDeskLink /> if this issue continues.
                </p>
            </WarningCallout>
            <div>
                <Button
                    type="button"
                    id="upload-retry-button"
                    onClick={() => navigate(routes.LLOYD_GEORGE_UPLOAD)}
                >
                    Try upload again
                </Button>
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
        </>
    );
}

export default LloydGeorgeRetryUploadStage;
