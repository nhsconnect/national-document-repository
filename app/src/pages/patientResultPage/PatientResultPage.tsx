import React, { useState } from 'react';
import { Button, WarningCallout } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import PatientSummary from '../../components/generic/patientSummary/PatientSummary';
import BackButton from '../../components/generic/backButton/BackButton';
import { useForm } from 'react-hook-form';
import ErrorBox from '../../components/layout/errorBox/ErrorBox';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import useRole from '../../helpers/hooks/useRole';
import usePatient from '../../helpers/hooks/usePatient';

function PatientResultPage() {
    const role = useRole();
    const patientDetails = usePatient();
    const userIsPCSE = role === REPOSITORY_ROLE.PCSE;
    const userIsGPAdmin = role === REPOSITORY_ROLE.GP_ADMIN;
    const userIsGPClinical = role === REPOSITORY_ROLE.GP_CLINICAL;
    const navigate = useNavigate();
    const [inputError, setInputError] = useState('');
    const { handleSubmit } = useForm();

    const submit = () => {
        if (userIsGPAdmin || userIsGPClinical) {
            // Make PDS patient search request to upload documents to patient
            if (typeof patientDetails?.active === 'undefined') {
                setInputError('We cannot determine the active state of this patient');
                return;
            }
            if (patientDetails?.active) {
                navigate(routes.LLOYD_GEORGE);
            } else {
                navigate(routes.ARF_UPLOAD_DOCUMENTS);
            }
        }

        // PCSE Role
        else if (userIsPCSE) {
            // Make PDS and Dynamo document store search request to download documents from patient
            navigate(routes.ARF_DOWNLOAD_DOCUMENTS);
        }
    };
    const showWarning = patientDetails?.superseded || patientDetails?.restricted;
    const isGp = userIsGPAdmin || userIsGPClinical;
    return (
        <div style={{ maxWidth: 730 }}>
            <BackButton />
            {inputError && (
                <ErrorBox
                    messageTitle={'There is a problem'}
                    messageLinkBody={inputError}
                    errorInputLink={'#patient-status'}
                    errorBoxSummaryId={'error-box-summary'}
                />
            )}
            <h1>Verify patient details</h1>

            {showWarning && (
                <WarningCallout>
                    <WarningCallout.Label headingLevel="h2">Information</WarningCallout.Label>
                    {patientDetails.superseded && (
                        <p>The NHS number for this patient has changed.</p>
                    )}
                    {patientDetails.restricted && (
                        <p>
                            Certain details about this patient cannot be displayed without the
                            necessary access.
                        </p>
                    )}
                </WarningCallout>
            )}

            <PatientSummary />

            <form onSubmit={handleSubmit(submit)} style={{ marginTop: 60 }}>
                {isGp && (
                    <>
                        <p id="gp-message">
                            Check these patient details match the records or attachments you plan to
                            use
                        </p>
                    </>
                )}
                <Button type="submit" id="verify-submit">
                    Accept details are correct
                </Button>
            </form>
            <p>
                If patient details are incorrect, please contact the{' '}
                <a
                    href="https://digital.nhs.uk/about-nhs-digital/contact-us#nhs-digital-service-desks"
                    target="_blank"
                    rel="noreferrer"
                >
                    NHS National Service Desk
                </a>
            </p>
        </div>
    );
}

export default PatientResultPage;
