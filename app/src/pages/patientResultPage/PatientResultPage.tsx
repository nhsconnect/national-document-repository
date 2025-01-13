import React, { useState } from 'react';
import { Button, WarningCallout } from 'nhsuk-react-components';
import { useNavigate } from 'react-router-dom';
import { routes } from '../../types/generic/routes';
import BackButton from '../../components/generic/backButton/BackButton';
import { useForm } from 'react-hook-form';
import ErrorBox from '../../components/layout/errorBox/ErrorBox';
import { REPOSITORY_ROLE } from '../../types/generic/authRole';
import useRole from '../../helpers/hooks/useRole';
import usePatient from '../../helpers/hooks/usePatient';
import useTitle from '../../helpers/hooks/useTitle';
import PatientSummary from '../../components/generic/patientSummary/PatientSummary';

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
            navigate(routes.ARF_OVERVIEW);
        }
    };
    const showWarning = patientDetails?.superseded || patientDetails?.restricted;
    const isGp = userIsGPAdmin || userIsGPClinical;
    const pageHeader = 'Patient details';
    useTitle({ pageTitle: pageHeader });
    return (
        <div style={{ maxWidth: 730 }}>
            <BackButton toLocation={routes.SEARCH_PATIENT} />
            {inputError && (
                <ErrorBox
                    messageTitle={'There is a problem'}
                    messageLinkBody={inputError}
                    errorInputLink={'#patient-status'}
                    errorBoxSummaryId={'error-box-summary'}
                />
            )}
            <h1>{pageHeader}</h1>

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
                            This page displays the current data recorded in the Patient Demographic
                            Service for this patient.
                        </p>
                    </>
                )}
                <Button type="submit" id="verify-submit" className="nhsuk-u-margin-top-6">
                    Confirm patient details and continue
                </Button>
            </form>
        </div>
    );
}

export default PatientResultPage;
