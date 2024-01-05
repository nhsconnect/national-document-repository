import WarningText from '../../components/generic/warningText/WarningText';
import { ButtonLink } from 'nhsuk-react-components';
import { MouseEventHandler } from 'react';

type Props = { next: MouseEventHandler<HTMLAnchorElement> };

const NonBsolLandingPage = ({ next }: Props) => {
    return (
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

            <WarningText>Downloading a record will remove it from our storage.</WarningText>

            <ButtonLink role="button" data-testid="start-btn" onClick={next}>
                Search for a patient
            </ButtonLink>

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
};

export default NonBsolLandingPage;
