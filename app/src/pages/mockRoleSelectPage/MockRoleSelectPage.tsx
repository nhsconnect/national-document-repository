import React, { useState } from 'react';
import { Button, Fieldset, Radios } from 'nhsuk-react-components';
import { FieldValues, useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { routes } from '../../types/generic/routes';
import ErrorBox from '../../components/layout/errorBox/ErrorBox';
import { useSessionContext } from '../../providers/sessionProvider/SessionProvider';
import { useOrganisationDetailsContext } from '../../providers/OrganisationProvider/OrganisationProvider';
import { OrganisationDetails } from '../../types/generic/organisationDetails';

function MockRoleSelectPage() {
    const [organisationDetails] = useOrganisationDetailsContext();
    console.log('organisationDetails =', organisationDetails);
    const organisationList: OrganisationDetails[] = organisationDetails ?? [];

    const navigate = useNavigate();
    const [inputError, setInputError] = useState('');
    const [session, setSession] = useSessionContext();
    const { handleSubmit, setValue, watch } = useForm();

    const submit = (fieldValues: FieldValues) => {
        const selectedOds = fieldValues.odsCode;

        if (!selectedOds) {
            setInputError('Select one organisation you would like to view');
            return;
        }

        const selected = organisationList.find((org) => org.odsCode === selectedOds);

        if (selected) {
            // You could store selected organisation in context or session here if needed
            console.log('Selected organisation:', selected);
        }

        setSession({
            ...session,
            isLoggedIn: true,
        });

        navigate(routes.SEARCH_PATIENT);
    };

    if (organisationList.length === 0) {
        return <p>Loading organisation details...</p>;
    }

    return (
        <div className="role-select-page-div">
            {inputError && (
                <ErrorBox
                    messageTitle="There is a problem"
                    messageLinkBody={inputError}
                    errorInputLink="#select-org-input"
                    errorBoxSummaryId="error-box-summary"
                />
            )}

            <form onSubmit={handleSubmit(submit)}>
                <Fieldset>
                    <Fieldset.Legend headingLevel="h1" isPageHeading>
                        Select an organisation
                    </Fieldset.Legend>

                    <Radios
                        id="select-org-input"
                        error={inputError}
                        hint="You are associated to more than one organisation. Select one to continue."
                    >
                        {organisationList.map((org) => (
                            <Radios.Radio
                                key={org.odsCode}
                                value={org.odsCode}
                                id={`radio-${org.odsCode}`}
                                name="organisation"
                                onChange={() => setValue('odsCode', org.odsCode)}
                                checked={watch('odsCode') === org.odsCode}
                            >
                                <p className="role-select-page-paragraph">{org.role}</p>
                                <p>
                                    [{org.odsCode}] {org.practiceName}
                                </p>
                            </Radios.Radio>
                        ))}
                    </Radios>
                </Fieldset>

                <Button type="submit" id="role-submit-button">
                    Continue
                </Button>
            </form>
        </div>
    );
}

export default MockRoleSelectPage;
