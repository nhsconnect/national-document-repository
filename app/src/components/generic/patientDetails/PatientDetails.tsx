import React from 'react';
import { SummaryList } from 'nhsuk-react-components';
import { getFormattedDate } from '../../../helpers/utils/formatDate';
import usePatient from '../../../helpers/hooks/usePatient';

const PatientDetails = () => {
    const patientDetails = usePatient();
    return (
        <SummaryList id="patient-details">
            <SummaryList.Row>
                <SummaryList.Key>NHS Number</SummaryList.Key>
                <SummaryList.Value id="patient-details-nhs-number">
                    {patientDetails?.nhsNumber}
                </SummaryList.Value>
            </SummaryList.Row>
            <SummaryList.Row>
                <SummaryList.Key>Surname</SummaryList.Key>
                <SummaryList.Value id="patient-details-family-name">
                    {patientDetails?.familyName}
                </SummaryList.Value>
            </SummaryList.Row>
            <SummaryList.Row>
                <SummaryList.Key>First name</SummaryList.Key>
                <SummaryList.Value id="patient-details-given-name">
                    {patientDetails?.givenName?.map((name) => `${name} `)}
                </SummaryList.Value>
            </SummaryList.Row>
            <SummaryList.Row>
                <SummaryList.Key>Date of birth</SummaryList.Key>
                <SummaryList.Value id="patient-details-date-of-birth">
                    {getFormattedDate(new Date(patientDetails?.birthDate ?? ''))}
                </SummaryList.Value>
            </SummaryList.Row>
            <SummaryList.Row>
                <SummaryList.Key>Postcode</SummaryList.Key>
                <SummaryList.Value id="patient-details-postcode">
                    {patientDetails?.postalCode}
                </SummaryList.Value>
            </SummaryList.Row>
        </SummaryList>
    );
};

export default PatientDetails;
