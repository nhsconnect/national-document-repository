import { ButtonLink } from 'nhsuk-react-components';
import { routes } from '../../../../types/generic/routes';
import { Link, useNavigate } from 'react-router-dom';
import useTitle from '../../../../helpers/hooks/useTitle';
import usePatient from '../../../../helpers/hooks/usePatient';
import { formatNhsNumber } from '../../../../helpers/utils/formatNhsNumber';
import { getFormattedDateFromString } from '../../../../helpers/utils/formatDate';
import { getFormattedPatientFullName } from '../../../../helpers/utils/formatPatientFullName';
import { JSX } from 'react';

const DocumentUploadCompleteStage = (): JSX.Element => {
    const navigate = useNavigate();
    const patientDetails = usePatient();
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const dob: string = getFormattedDateFromString(patientDetails?.birthDate);
    const patientName = getFormattedPatientFullName(patientDetails);

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
                    <strong data-testid="patient-name">Patient name: {patientName}</strong>
                    <br />
                    <span data-testid="nhs-number">NHS Number: {formattedNhsNumber}</span>
                    <br />
                    <span data-testid="dob">Date of birth: {dob}</span>
                </div>
            </div>

            <h2>What happens next</h2>
            <p>
                You can now view this patient's record within this service by{' '}
                <Link
                    to=""
                    onClick={(e): void => {
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
                For information on destroying your paper records and removing the digital files from
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
                onClick={(e): void => {
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
