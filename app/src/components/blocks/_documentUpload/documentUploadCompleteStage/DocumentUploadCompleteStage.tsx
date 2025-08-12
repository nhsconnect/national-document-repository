import { ButtonLink } from 'nhsuk-react-components';
import { routes } from '../../../../types/generic/routes';
import { Link, useNavigate } from 'react-router-dom';
import useTitle from '../../../../helpers/hooks/useTitle';
import usePatient from '../../../../helpers/hooks/usePatient';
import { getFormattedDate } from '../../../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';

const DocumentUploadCompleteStage = () => {
    const navigate = useNavigate();
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const dob: string = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';

    useTitle({ pageTitle: 'Record upload complete' });

    return (
        <div className="lloydgeorge_upload-complete" data-testid="upload-complete-page">
            <div className="nhsuk-panel" data-testid="upload-complete-card">
                <h1 className="nhsuk-panel__title">Upload complete</h1>
                <div className="nhsuk-panel__body">
                    You have successfully uploaded a digital Lloyd George record for:
                </div>
                <br />
                <div className="nhsuk-panel__body">
                    <strong>
                        Patient name: {patientDetails?.familyName}, {patientDetails?.givenName}
                    </strong>
                    <br />
                    <span>NHS Number: {formattedNhsNumber}</span>
                    <br />
                    <span>Date of birth: {dob}</span>
                </div>
            </div>

            <h2>What happens next</h2>
            <p>
                You can now view this patient's record within this service by{' '}
                <Link
                    to=""
                    onClick={(e) => {
                        e.preventDefault();
                        navigate(routes.SEARCH_PATIENT);
                    }}
                    data-testid="search-patient-link"
                >
                    searching using their NHS number
                </Link>
                {'.'}
            </p>

            <p>
                For information on destroying your paper records an removing the digital files from
                your system, read the article{' '}
                <Link
                    to="https://future.nhs.uk/DigitalPC/view?objectId=185217477"
                    data-testid="digitisation-link"
                >
                    Digitisation of Lloyd George records
                </Link>
                {'.'}
            </p>

            <ButtonLink
                data-testid="home-btn"
                role="button"
                href="#"
                onClick={(e) => {
                    e.preventDefault();
                    navigate(routes.HOME);
                }}
            >
                Go to home
            </ButtonLink>
        </div>
    );
};

export default DocumentUploadCompleteStage;
