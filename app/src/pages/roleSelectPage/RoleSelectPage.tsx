import React, { useState } from 'react';
import { Button, Fieldset, Radios } from 'nhsuk-react-components';
import { FieldValues, useForm } from 'react-hook-form';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import ErrorBox from '../../components/layout/errorBox/ErrorBox';

type Props = {};

function RoleSelectPage({}: Props) {
    const navigate = useNavigate();
    const [inputError, setInputError] = useState('');

    const { register, handleSubmit, formState, getFieldState } = useForm();
    const { ref: organisationRef, ...radioProps } = register('organisation');
    const { isDirty: isOrganisationDirty } = getFieldState('organisation', formState);

    const submit = (fieldValues: FieldValues) => {
        if (!isOrganisationDirty) {
            setInputError('Select one organisation you would like to view');
            return;
        }
        if (fieldValues.organisation === 'PCSE') {
            navigate(routes.DOWNLOAD_SEARCH);
        } else if (fieldValues.organisation === 'GP') {
            navigate(routes.UPLOAD_SEARCH);
        }
    };

    return (
        <div style={{ maxWidth: 730 }}>
            {inputError && (
                <ErrorBox
                    messageTitle={'There is a problem'}
                    messageLinkBody={inputError}
                    errorInputLink={'#select-org-input'}
                    errorBoxSummaryId={'error-box-summary'}
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
                        hint="You are associated to more than one organisation, select an organisation you would like to view."
                    >
                        <Radios.Radio value={'GP'} inputRef={organisationRef} {...radioProps}>
                            <p style={{ margin: 0, fontWeight: 'bold' }}>GP Role</p>
                            <p>{'[A9A5A] GP Practice'}</p>
                        </Radios.Radio>
                        <Radios.Radio value={'PCSE'} inputRef={organisationRef} {...radioProps}>
                            <p style={{ margin: 0, fontWeight: 'bold' }}>PCSE Role</p>
                            <p>{'[B9A5A] Primary Care Support England'}</p>
                        </Radios.Radio>
                    </Radios>
                </Fieldset>
                <Button type="submit">Continue</Button>
            </form>
        </div>
    );
}

export default RoleSelectPage;
