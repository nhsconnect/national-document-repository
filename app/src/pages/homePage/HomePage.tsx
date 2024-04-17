import WarningText from '../../components/generic/warningText/WarningText';
import { ButtonLink } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import useIsBSOL from '../../helpers/hooks/useIsBSOL';
import React, { useEffect } from 'react';
import useRole from '../../helpers/hooks/useRole';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import ServiceDeskLink from '../../components/generic/serviceDeskLink/ServiceDeskLink';
import pageTitle from '../../components/layout/pageTitle/PageTitle';

type Props = {};

const RedirectToSearchPage = () => {
    const navigate = useNavigate();
    useEffect(() => {
        navigate(routes.SEARCH_PATIENT);
    });
    return <></>;
};

const HomePage = (props: Props) => {
    const navigate = useNavigate();
    const isBsol = useIsBSOL();

    const role = useRole();
    const userIsPCSE = role === REPOSITORY_ROLE.PCSE;

    const SearchButton = () => (
        <ButtonLink
            role="button"
            data-testid="search-patient-btn"
            href="#"
            onClick={(e) => {
                e.preventDefault();
                navigate(routes.SEARCH_PATIENT);
            }}
        >
            Search for a patient
        </ButtonLink>
    );

    const NonBsolContent = () => {
        pageTitle({ pageTitle: 'Access to this service outside of Birmingham and Solihull' });
        return (
            <>
                <h1>You’re outside of Birmingham and Solihull (BSOL)</h1>
                <p>
                    As you’re outside Birmingham and Solihull, the pilot area for this service, you
                    can use this service to:
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
                <ServiceDeskLink />
                {' if there is an issue with this service or call 0300 303 5678.'}
            </>
        );
    };

    return isBsol || userIsPCSE ? <RedirectToSearchPage /> : <NonBsolContent />;
};

export default HomePage;
