import React, { useState } from 'react';
import useBaseAPIHeaders from '../../helpers/hooks/useBaseAPIHeaders';
import useBaseAPIUrl from '../../helpers/hooks/useBaseAPIUrl';
import usePatient from '../../helpers/hooks/usePatient';
import BackButton from '../../components/generic/backButton/BackButton';

import { getFormattedDate } from '../../helpers/utils/formatDate';
import { formatNhsNumber } from '../../helpers/utils/formatNhsNumber';
import { Button, Table, WarningCallout } from 'nhsuk-react-components';
import getLloydGeorgeAnalysis from '../../helpers/requests/getLloydGeorgeAnalysis';
import { AxiosError } from 'axios';
import { routes } from '../../types/generic/routes';
import { errorToParams } from '../../helpers/utils/errorToParams';
import { useNavigate } from 'react-router-dom';
import { isMock } from '../../helpers/utils/isLocal';

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
    const [searchResults, setSearchResults] = useState<SearchResult>();
    const [activePanel, setActivePanel] = useState<string>('Medication');
    const analyseLG = async () => {
        try {
            const results = await getLloydGeorgeAnalysis({
                baseUrl,
                baseHeaders,
                nhsNumber,
            });
            setSearchResults(results ?? []);
        } catch (e) {
            const error = e as AxiosError;

            if (isMock(error)) {
                const results = await fetch('/analyses.json').then((r) => r.json());
                setSearchResults(results ?? []);
                return;
            }
            navigate(routes.SERVER_ERROR + errorToParams(error));
        }
    };
    const medicalInfo = searchResults?.PROTECTED_HEALTH_INFORMATION ?? {};
    const medications = searchResults?.MEDICATION ?? {};
    const medicalConditions = searchResults?.MEDICAL_CONDITION ?? {};
    const anatomy = searchResults?.ANATOMY ?? {};
    const treatmentProcedure = searchResults?.TEST_TREATMENT_PROCEDURE ?? {};
    const getMedicalInfoName = Object.keys(medicalInfo).find((info: string) => {
        const type = medicalInfo[info][0].Type;
        return type === 'NAME';
    });
    const getMedicalInfoNhsNumber = Object.keys(medicalInfo).find((info: string) => {
        const type = medicalInfo[info][0].Type;

        return type === 'ID' && info.length === 10;
    });
    const getPageNumbers = (analysisObject: AnalysisFields[]) => {
        return analysisObject.reduce((acc: number[], curr) => {
            if (!acc.includes(curr.PageNumber)) acc.push(curr.PageNumber);
            return acc;
        }, []);
    };
    const table_header = (
        <Table.Head>
            <Table.Row>
                <Table.Cell>Keyword</Table.Cell>
                <Table.Cell>Page numbers</Table.Cell>
            </Table.Row>
        </Table.Head>
    );
    return (
        <div>
            <BackButton />
            <h1>Medical analysis results</h1>
            <div id="patient-info" className="lloydgeorge_record-stage_patient-info">
                <p data-testid="patient-name">
                    {`${patientDetails?.givenName} ${patientDetails?.familyName}`}
                </p>
                <p data-testid="patient-nhs-number">NHS number: {formattedNhsNumber}</p>
                <p data-testid="patient-dob">Date of birth: {dob}</p>
            </div>
            {!searchResults ? (
                <Button type="button" id="upload-button" onClick={() => analyseLG()}>
                    Start Analysis
                </Button>
            ) : (
                <div>
                    {medicalInfo ? (
                        <WarningCallout>
                            <WarningCallout.Label>Patient Information found</WarningCallout.Label>
                            <p>
                                During the analysis on this patient's document the following
                                personal information was found:
                                <p></p>
                                <ul>
                                    <li>Name: {getMedicalInfoName}</li>
                                    <li>NHS number: {getMedicalInfoNhsNumber}</li>
                                </ul>
                                If this information does not belong to this patient please contact
                                the service desk.
                            </p>
                        </WarningCallout>
                    ) : (
                        <></>
                    )}
                    <div className="nhsuk-tabs" data-module="nhsuk-tabs">
                        <h2 className="nhsuk-tabs__title">Contents</h2>
                        <ul className="nhsuk-tabs__list">
                            <li
                                className={
                                    activePanel === 'Medication'
                                        ? 'nhsuk-tabs__list-item nhsuk-tabs__list-item--selected'
                                        : 'nhsuk-tabs__list-item'
                                }
                            >
                                <a
                                    className="nhsuk-tabs__tab"
                                    onClick={() => setActivePanel('Medication')}
                                >
                                    Medications
                                </a>
                            </li>

                            <li
                                className={
                                    activePanel === 'Medical-conditions'
                                        ? 'nhsuk-tabs__list-item nhsuk-tabs__list-item--selected'
                                        : 'nhsuk-tabs__list-item'
                                }
                            >
                                <a
                                    className="nhsuk-tabs__tab"
                                    onClick={() => setActivePanel('Medical-conditions')}
                                >
                                    Medical conditions
                                </a>
                            </li>

                            <li
                                className={
                                    activePanel === 'Anatomy'
                                        ? 'nhsuk-tabs__list-item nhsuk-tabs__list-item--selected'
                                        : 'nhsuk-tabs__list-item'
                                }
                            >
                                <a
                                    className="nhsuk-tabs__tab"
                                    onClick={() => setActivePanel('Anatomy')}
                                >
                                    Anatomy
                                </a>
                            </li>

                            <li
                                className={
                                    activePanel === 'Test-treatment-procedure'
                                        ? 'nhsuk-tabs__list-item nhsuk-tabs__list-item--selected'
                                        : 'nhsuk-tabs__list-item'
                                }
                            >
                                <a
                                    className="nhsuk-tabs__tab"
                                    onClick={() => setActivePanel('Test-treatment-procedure')}
                                >
                                    Test treatment procedure
                                </a>
                            </li>
                        </ul>
                        <div
                            className={
                                activePanel === 'Medication'
                                    ? 'nhsuk-tabs__panel'
                                    : 'nhsuk-tabs__panel--hidden'
                            }
                            id="Medication"
                        >
                            <Table
                                responsive
                                caption="Medications"
                                captionProps={{
                                    className: 'nhsuk-table__caption',
                                }}
                            >
                                {table_header}
                                <Table.Body>
                                    {Object.keys(medications).map((medication: string) => {
                                        const pageNumbers: number[] = getPageNumbers(
                                            medications[medication],
                                        );
                                        return (
                                            <Table.Row key={medication}>
                                                <Table.Cell>
                                                    <div>{medication}</div>
                                                </Table.Cell>
                                                <Table.Cell>{pageNumbers.join()}</Table.Cell>
                                            </Table.Row>
                                        );
                                    })}
                                </Table.Body>{' '}
                            </Table>
                        </div>
                        <div
                            className={
                                activePanel === 'Medical-conditions'
                                    ? 'nhsuk-tabs__panel'
                                    : 'nhsuk-tabs__panel--hidden'
                            }
                            id="Medical-conditions"
                        >
                            <Table
                                responsive
                                caption="Medical conditions"
                                captionProps={{
                                    className: 'nhsuk-table__caption',
                                }}
                                id="Medical-conditions"
                            >
                                {table_header}

                                <Table.Body>
                                    {Object.keys(medicalConditions).map((condition: string) => {
                                        const pageNumbers = getPageNumbers(
                                            medicalConditions[condition],
                                        );
                                        return (
                                            <Table.Row key={condition}>
                                                <Table.Cell>
                                                    <div>{condition}</div>
                                                </Table.Cell>
                                                <Table.Cell>{pageNumbers.join()}</Table.Cell>
                                            </Table.Row>
                                        );
                                    })}
                                </Table.Body>
                            </Table>{' '}
                        </div>
                        <div
                            className={
                                activePanel === 'Anatomy'
                                    ? 'nhsuk-tabs__panel'
                                    : 'nhsuk-tabs__panel--hidden'
                            }
                            id="Anatomy"
                        >
                            <Table
                                responsive
                                caption="Anatomy"
                                captionProps={{
                                    className: 'nhsuk-table__caption',
                                }}
                                id="Anatomy"
                            >
                                {table_header}
                                <Table.Body>
                                    {Object.keys(anatomy).map((anatomyKey: string) => {
                                        const pageNumbers = getPageNumbers(anatomy[anatomyKey]);
                                        return (
                                            <Table.Row key={anatomyKey}>
                                                <Table.Cell>
                                                    <div>{anatomyKey}</div>
                                                </Table.Cell>
                                                <Table.Cell>{pageNumbers.join()}</Table.Cell>
                                            </Table.Row>
                                        );
                                    })}
                                </Table.Body>{' '}
                            </Table>
                        </div>
                        <div
                            className={
                                activePanel === 'Test-treatment-procedure'
                                    ? 'nhsuk-tabs__panel'
                                    : 'nhsuk-tabs__panel--hidden'
                            }
                            id="Test-treatment-procedure"
                        >
                            <Table
                                responsive
                                caption="Treatment Procedure"
                                captionProps={{
                                    className: 'nhsuk-table__caption',
                                }}
                                id="treatmentProcedure"
                            >
                                {table_header}
                                <Table.Body>
                                    {Object.keys(treatmentProcedure).map(
                                        (treatmentProcedureKey: string) => {
                                            const pageNumbers = getPageNumbers(
                                                treatmentProcedure[treatmentProcedureKey],
                                            );
                                            return (
                                                <Table.Row key={treatmentProcedureKey}>
                                                    <Table.Cell>
                                                        <div>{treatmentProcedureKey}</div>
                                                    </Table.Cell>
                                                    <Table.Cell>{pageNumbers.join()}</Table.Cell>
                                                </Table.Row>
                                            );
                                        },
                                    )}
                                </Table.Body>{' '}
                            </Table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default LloydGeorgeMedicalSummaryPage;
