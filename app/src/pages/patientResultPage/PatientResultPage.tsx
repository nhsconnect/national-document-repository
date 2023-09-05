import React, { useEffect } from 'react';
import { USER_ROLE } from '../../types/generic/roles';
import { Button, WarningCallout } from 'nhsuk-react-components';
import { useNavigate } from 'react-router';
import { routes } from '../../types/generic/routes';
import PatientSummary from '../../components/generic/patientSummary/PatientSummary';
import { usePatientDetailsContext } from '../../providers/patientProvider/PatientProvider';

type Props = {
    role: USER_ROLE;
};

function PatientResultPage({ role }: Props) {
    const userIsPCSE = role === USER_ROLE.PCSE;
    const userIsGP = role === USER_ROLE.GP;
    const [patientDetails] = usePatientDetailsContext();
    const navigate = useNavigate();

    useEffect(() => {
        if (!patientDetails) {
            navigate(routes.HOME);
        }
    }, [patientDetails, navigate]);

    const handleVerify = () => {
        if (userIsGP) {
            // Make PDS patient search request to upload documents to patient
            navigate(routes.UPLOAD_DOCUMENTS);
        }

        // PCSE Role
        else if (userIsPCSE) {
            // Make PDS and Dynamo document store search request to download documents from patient
            navigate(routes.DOWNLOAD_DOCUMENTS);
        }
    };
    return (
        <div style={{ maxWidth: 500 }}>
            <h1>Verify patient details</h1>
            {patientDetails && (patientDetails.superseded || patientDetails.restricted) && (
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
            {patientDetails && <PatientSummary patientDetails={patientDetails} />}
            {userIsGP && (
                <p>
                    Ensure these patient details match the electronic health records and attachments
                    you are about to upload.
                </p>
            )}

            <Button onClick={handleVerify} id="verify-submit">
                Accept details are correct
            </Button>
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
