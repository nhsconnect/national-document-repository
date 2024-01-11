import WarningText from '../../components/generic/warningText/WarningText';
import { ButtonLink } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import useIsBSOL from '../../helpers/hooks/useIsBSOL';
import useRole from '../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';

type Props = {};

const HomePage = (props: Props) => {
    const navigate = useNavigate();
    const { GP_ADMIN, GP_CLINICAL } = REPOSITORY_ROLE;
    const isBsol = useIsBSOL();
    const role = useRole();

    const SearchButton = () => (
        <ButtonLink
            role="button"
            data-testid="search-patient-btn"
            onClick={() => {
                if (role && [GP_ADMIN, GP_CLINICAL].includes(role)) {
                    navigate(routes.UPLOAD_SEARCH);
                } else {
                    navigate(routes.DOWNLOAD_SEARCH);
                }
            }}
        >
            Search for a patient
        </ButtonLink>
    );

    const BsolContent = () => (
        <>
            <h1>Access and store digital GP records</h1>
            <p>
                This service gives you access to Lloyd George digital health records. You may have
                received a note within a patient record, stating that the record has been digitised.
            </p>
            <p>If you are part of a GP practice, you can use this service to:</p>
            <ul>
                <li>view a patient record</li>
                <li>download a patient record</li>
                <li>remove a patient record</li>
            </ul>
            <p>If you are managing records on behalf of NHS England, you can:</p>
            <ul>
                <li>download a patient record</li>
            </ul>
            <p>Not every patient will have a digital record available.</p>
            <h2>Before you start</h2>
            <p>You’ll be asked for:</p>
            <ul>
                <li>your NHS smartcard</li>
                <li>patient details including their name, date of birth and NHS number</li>
            </ul>

            <SearchButton />
            <h3>Get support with the service</h3>
            {'Contact the '}
            <a
                href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                target="_blank"
                rel="noreferrer"
            >
                NHS National Service Desk
            </a>
            {' if there is an issue with this service or call 0300 303 5678.'}
        </>
    );

    const NonBsolContent = () => (
        <>
            <h1>You’re outside of Birmingham and Solihull (BSOL)</h1>
            <p>
                As you’re outside Birmingham and Solihull, the pilot area for this service, you can
                use this service to:
            </p>

            <ul>
                <li>view records if the patient joins your practice</li>

                <li>download records if a patient leaves your practice</li>
            </ul>
            <p>You’ll be asked for patient details, including their:</p>
            <ul>
                <li>name</li>
                <li>date of birth</li>
                <li>NHS number</li>
            </ul>

            <WarningText text="Downloading a record will remove it from our storage." />

            <SearchButton />

            <h3>Get support with the service</h3>
            {'Contact the '}
            <a
                href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                target="_blank"
                rel="noreferrer"
            >
                NHS National Service Desk
            </a>
            {' if there is an issue with this service or call 0300 303 5678.'}
        </>
    );

    return isBsol ? <BsolContent /> : <NonBsolContent />;
};

export default HomePage;
