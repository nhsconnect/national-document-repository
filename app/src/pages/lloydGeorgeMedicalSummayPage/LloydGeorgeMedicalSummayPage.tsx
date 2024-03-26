import React, { useState } from 'react';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import usePatient from '../../helpers/hooks/usePatient';
import BackButton from '../../components/generic/backButton/BackButton';

import { getFormattedDate } from '../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../helpers/utils/formatNhsNumber';
import { Button, Table } from 'nhsuk-react-components';
import getLloydGeorgeAnalysis from '../../helpers/requests/getLloydGeorgeAnalysis';
import { AxiosError } from 'axios';
import { routes } from '../../types/generic/routes';
import { errorToParams } from '../../helpers/utils/errorToParams';
import { useNavigate } from 'react-router-dom';

export type SearchResult = {
    MEDICATION: AnalysisKey;
    PROTECTED_HEALTH_INFORMATION: AnalysisKey;
    TEST_TREATMENT_PROCEDURE: AnalysisKey;
    ANATOMY: AnalysisKey;
    MEDICAL_CONDITION: AnalysisKey;
};
export type AnalysisKey = {
    [key: string]: [AnalysisFields];
};

export type AnalysisFields = {
    Id: number;
    BeginOffset: number;
    EndOffset: number;
    Score: number;
    Text: string;
    Category: string;
    Type: string;
    Traits: [
        {
            Name: string;
            Score: number;
        },
    ];
    PageNumber: number;
};

function LloydGeorgeMedicalSummaryPage() {
    const patientDetails = usePatient();
    const baseUrl = useBaseAPIUrl();
    const navigate = useNavigate();

    const baseHeaders = useBaseAPIHeaders();
    const dob: string = patientDetails?.birthDate
        ? getFormattedDate(new Date(patientDetails.birthDate))
        : '';
    const nhsNumber: string = patientDetails?.nhsNumber ?? '';
    const formattedNhsNumber = formatNhsNumber(nhsNumber);
    const [isAnalysingDocuments, setIsAnalysingDocuments] = useState(false);
    const [searchResults, setSearchResults] = useState<SearchResult>();

    const analyseLG = async () => {
        try {
            const results = await getLloydGeorgeAnalysis({
                baseUrl,
                baseHeaders,
            });
            setIsAnalysingDocuments(true);
            setSearchResults(results ?? []);
        } catch (e) {
            const error = e as AxiosError;
            navigate(routes.SERVER_ERROR + errorToParams(error));
        }
    };
    const medications = searchResults?.MEDICATION ?? {};

    return !isAnalysingDocuments ? (
        <Button type="button" id="upload-button" onClick={() => analyseLG}>
            Some text
        </Button>
    ) : (
        <div className="lloydgeorge_record-stage">
            <BackButton />

            <div id="patient-info" className="lloydgeorge_record-stage_patient-info">
                <p data-testid="patient-name">
                    {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
                </p>
                <p data-testid="patient-nhs-number">NHS number: {formattedNhsNumber}</p>
                <p data-testid="patient-dob">Date of birth: {dob}</p>
            </div>
            <div className="nhsuk-tabs" data-module="nhsuk-tabs">
                <h2 className="nhsuk-tabs__title">Contents</h2>

                <ul className="nhsuk-tabs__list">
                    <li className="nhsuk-tabs__list-item nhsuk-tabs__list-item--selected">
                        <a className="nhsuk-tabs__tab" href="#Medication">
                            Medications
                        </a>
                    </li>

                    <li className="nhsuk-tabs__list-item">
                        <a className="nhsuk-tabs__tab" href="#Medical-conditions">
                            Medical conditions
                        </a>
                    </li>

                    <li className="nhsuk-tabs__list-item">
                        <a className="nhsuk-tabs__tab" href="#Anatomy">
                            Anatomy
                        </a>
                    </li>

                    <li className="nhsuk-tabs__list-item">
                        <a className="nhsuk-tabs__tab" href="#Test-treatment-procedure">
                            Test treatment procedure
                        </a>
                    </li>
                </ul>

                <div className="nhsuk-tabs__panel" id="Medication">
                    <Table.Body>
                        {Object.keys(medications).map((medication: string) => {
                            const pageNumbers = medications[medication].map(
                                (field) => field.PageNumber,
                            );
                            return (
                                <Table.Row key={medication}>
                                    <Table.Cell>
                                        <div>{medication}</div>
                                    </Table.Cell>
                                    <Table.Cell>{pageNumbers}</Table.Cell>
                                </Table.Row>
                            );
                        })}
                    </Table.Body>{' '}
                </div>

                <div
                    className="nhsuk-tabs__panel nhsuk-tabs__panel--hidden"
                    id="Medical-conditions"
                ></div>

                <div className="nhsuk-tabs__panel nhsuk-tabs__panel--hidden" id="Anatomy"></div>

                <div
                    className="nhsuk-tabs__panel nhsuk-tabs__panel--hidden"
                    id="Test-treatment-procedure"
                ></div>
            </div>
        </div>
    );
}

export default LloydGeorgeMedicalSummaryPage;
