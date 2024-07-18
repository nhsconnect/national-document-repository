import viewLloydGeorgePayload from '../../../fixtures/requests/GET_LloydGeorgeStitch.json';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatient.json';
import { Roles } from '../../../support/roles';
import { formatNhsNumber } from '../../../../src/helpers/utils/formatNhsNumber';

const baseUrl = Cypress.config('baseUrl');
const patientSearchUrl = '/patient/search';

const downloadPageTitle =
    'Download the Lloyd George record for this patient - Digital Lloyd George records';
const downloadingPageTitle = 'Downloading documents - Digital Lloyd George records';
const downloadCompletePageTitle = 'Download complete - Digital Lloyd George records';
const verifyPatientPageTitle = 'Verify patient details - Digital Lloyd George records';
const lloydGeorgeRecordPageTitle = 'Available records - Digital Lloyd George records';
const testFiles = [
    {
        fileName: '1of2_testy_test.pdf',
        created: '2024-05-07T14:52:00.827602Z',
        virusScannerResult: 'Clean',
        id: 'test-id',
    },
    {
        fileName: '2of2_testy_test.pdf',
        created: '2024-05-07T14:52:00.827602Z',
        virusScannerResult: 'Clean',
        id: 'test-id-2',
    },
    {
        fileName: '1of1_lone_test_file.pdf',
        created: '2024-01-01T14:52:00.827602Z',
        virusScannerResult: 'Clean',
        id: 'test-id-3',
    },
];

const singleTestFile = [
    {
        fileName: '1of1_lone_test_file.pdf',
        created: '2024-01-01T14:52:00.827602Z',
        virusScannerResult: 'Clean',
        id: 'test-id-3',
    },
];

describe('GP Workflow: View Lloyd George record', () => {
    const beforeEachConfiguration = (role) => {
        cy.login(role);
        cy.visit(patientSearchUrl);

        // search patient
        cy.intercept('GET', '/SearchPatient*', {
            statusCode: 200,
            body: searchPatientPayload,
        }).as('search');
        cy.getByTestId('nhs-number-input').type(searchPatientPayload.nhsNumber);
        cy.getByTestId('search-submit-btn').click();
        cy.wait('@search');
    };

    const setUpDownloadManifestIntercepts = () => {
        let getPollingCount = 0;
        const jobId = 'test-jobId';

        cy.intercept('POST', '/DocumentManifest*', (req) => {
            req.reply({
                statusCode: 200,
                body: { jobId: jobId },
            });
        }).as('documentManifestPost');

        cy.intercept(
            {
                method: 'GET',
                url: '/DocumentManifest*',
                query: {
                    jobId: jobId,
                },
            },
            (req) => {
                getPollingCount += 1;
                if (getPollingCount < 3) {
                    req.reply({
                        statusCode: 200,
                        body: { jobStatus: 'Processing', url: '' },
                    });
                    req.alias = 'documentManifestProcessing';
                } else {
                    req.reply({
                        statusCode: 200,
                        body: { jobStatus: 'Completed', url: baseUrl + '/browserconfig.xml' }, // uses public served file in place of a ZIP file
                    });
                    req.alias = 'documentManifestCompleted';
                }
            },
        );
    };

    const proceedToDownloadSelectionPage = () => {
        cy.intercept('GET', '/LloydGeorgeStitch*', {
            statusCode: 200,
            body: viewLloydGeorgePayload,
        }).as('lloydGeorgeStitch');

        cy.intercept('GET', '/SearchDocumentReferences*', {
            statusCode: 200,
            body: testFiles,
        }).as('searchDocumentReferences');

        cy.get('#verify-submit').click();
        cy.wait('@lloydGeorgeStitch');

        cy.getByTestId('download-all-files-link').click();
    };

    context('Download Lloyd George document', () => {
        it(
            'GP ADMIN user can download the entire Lloyd George document of an active patient',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);

                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 200,
                    body: viewLloydGeorgePayload,
                }).as('lloydGeorgeStitch');

                cy.intercept('GET', '/SearchDocumentReferences*', {
                    statusCode: 200,
                    body: testFiles,
                }).as('searchDocumentReferences');

                setUpDownloadManifestIntercepts();

                cy.title().should('eq', verifyPatientPageTitle);

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');
                cy.title().should('eq', lloydGeorgeRecordPageTitle);

                cy.getByTestId('download-all-files-link').should('exist');
                cy.getByTestId('download-all-files-link').click();

                // Select documents page
                cy.title().should('eq', downloadPageTitle);
                cy.wait('@searchDocumentReferences');

                cy.getByTestId('patient-summary').should('exist');

                cy.getByTestId('available-files-table-title').should('exist');
                cy.getByTestId('download-selected-files-btn').should('exist');
                cy.getByTestId('toggle-selection-btn').should('exist');

                cy.getByTestId('start-again-link').should('exist');
                cy.getByTestId('toggle-selection-btn').click();
                cy.getByTestId('download-selected-files-btn').click();

                cy.title().should('eq', downloadingPageTitle);

                // Assert contents of page when downloading
                cy.getByTestId('lloyd-george-download-header').should('exist');
                cy.getByTestId('cancel-download-link').should('exist');
                cy.getByTestId('download-file-header-' + testFiles.length + '-files').should(
                    'exist',
                );

                // Assert contents of page after download
                cy.wait('@documentManifestCompleted');
                cy.title().should('eq', downloadCompletePageTitle);
                cy.getByTestId('downloaded-record-card-header').should('exist');
                cy.contains(
                    `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
                ).should('be.visible');
                cy.contains(formatNhsNumber(searchPatientPayload.nhsNumber)).should('be.visible');
                cy.getByTestId('downloaded-files-' + testFiles.length + '-files').should(
                    'not.exist',
                );

                // Assert file has been downloaded
                cy.readFile(`${Cypress.config('downloadsFolder')}/browserconfig.xml`);

                cy.getByTestId('return-btn').click();

                // Assert return button returns to pdf view
                cy.getByTestId('pdf-card').should('be.visible');
            },
        );

        it(
            'GP ADMIN user can selectively download a portion of Lloyd George document of an active patient',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);
                setUpDownloadManifestIntercepts();
                proceedToDownloadSelectionPage();

                // Select documents page
                cy.title().should('eq', downloadPageTitle);
                cy.wait('@searchDocumentReferences');

                cy.getByTestId('download-selected-files-btn').should('exist');
                cy.getByTestId('toggle-selection-btn').should('exist');

                cy.getByTestId('checkbox-0').should('exist');
                cy.getByTestId('checkbox-1').should('exist');
                cy.getByTestId('checkbox-2').should('exist');

                cy.getByTestId('checkbox-0').click();
                cy.getByTestId('checkbox-1').click();

                cy.getByTestId('download-selected-files-btn').click();

                // Assert contents of page when downloading
                cy.title().should('eq', downloadingPageTitle);
                // Assert contents of page when downloading
                cy.getByTestId('lloyd-george-download-header').should('exist');
                cy.getByTestId('download-file-header-2-files').should('exist');

                cy.getByTestId('cancel-download-link').should('exist');

                // Assert contents of page after download
                cy.wait('@documentManifestCompleted');
                cy.title().should('eq', downloadCompletePageTitle);
                cy.getByTestId('downloaded-files-card-header').should('exist');
                cy.contains(
                    `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
                ).should('be.visible');
                cy.getByTestId('downloaded-files-2-files').should('exist');

                cy.contains(formatNhsNumber(searchPatientPayload.nhsNumber)).should('be.visible');

                // Assert file has been downloaded
                cy.readFile(`${Cypress.config('downloadsFolder')}/browserconfig.xml`);

                cy.getByTestId('return-btn').click();

                // Assert return button returns to pdf view
                cy.getByTestId('pdf-card').should('be.visible');
            },
        );

        it(
            'GP ADMIN user can download entire Lloyd George document when single file',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);

                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 200,
                    body: viewLloydGeorgePayload,
                }).as('lloydGeorgeStitch');

                cy.intercept('GET', '/SearchDocumentReferences*', {
                    statusCode: 200,
                    body: singleTestFile,
                }).as('searchDocumentReferences');

                setUpDownloadManifestIntercepts();

                cy.title().should('eq', verifyPatientPageTitle);

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');
                cy.title().should('eq', lloydGeorgeRecordPageTitle);

                cy.getByTestId('download-all-files-link').should('exist');
                cy.getByTestId('download-all-files-link').click();

                // Select documents page
                cy.title().should('eq', downloadPageTitle);
                cy.wait('@searchDocumentReferences');

                cy.getByTestId('patient-summary').should('exist');

                cy.getByTestId('available-files-table-title').should('exist');
                cy.getByTestId('download-file-btn').should('exist');

                cy.getByTestId('download-file-btn').click();

                // Assert contents of page when downloading
                cy.title().should('eq', downloadingPageTitle);
                // Assert contents of page when downloading
                cy.getByTestId('lloyd-george-download-header').should('exist');
                cy.getByTestId('download-file-header-1-files').should('exist');

                cy.getByTestId('cancel-download-link').should('exist');

                // Assert contents of page after download
                cy.wait('@documentManifestCompleted');
                cy.title().should('eq', downloadCompletePageTitle);
                cy.getByTestId('downloaded-record-card-header').should('exist');
                cy.contains(
                    `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
                ).should('be.visible');

                cy.contains(formatNhsNumber(searchPatientPayload.nhsNumber)).should('be.visible');

                // Assert file has been downloaded
                cy.readFile(`${Cypress.config('downloadsFolder')}/browserconfig.xml`);

                cy.getByTestId('return-btn').click();

                // Assert return button returns to pdf view
                cy.getByTestId('pdf-card').should('be.visible');
            },
        );

        it(
            'should display an alert if user click "Download selected files" without selecting anything',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);
                setUpDownloadManifestIntercepts();
                proceedToDownloadSelectionPage();

                // Select documents page
                cy.title().should('eq', downloadPageTitle);
                cy.wait('@searchDocumentReferences');

                cy.getByTestId('download-selected-files-btn').should('exist');
                cy.getByTestId('download-selected-files-btn').click();

                cy.title().should('not.equal', downloadingPageTitle);
                cy.title().should('equal', downloadPageTitle);

                cy.get('#error-box-summary').should('be.visible');
                cy.get('.nhsuk-error-summary__body').should('be.visible');
                cy.getByTestId('download-selection-error-box').should('exist');
            },
        );

        it('should display an error page when download manifest API responded with PENDING for 3 times', () => {
            let pendingCounts = 0;
            beforeEachConfiguration(Roles.GP_ADMIN);

            cy.intercept('POST', '/DocumentManifest*', (req) => {
                req.reply({
                    statusCode: 200,
                    body: { jobId: 'testJobId' },
                });
            }).as('documentManifestPost');

            cy.intercept('GET', '/DocumentManifest*', (req) => {
                pendingCounts += 1;
                req.reply({
                    statusCode: 200,
                    body: { jobStatus: 'Pending' },
                });
                if (pendingCounts >= 3) {
                    req.alias = 'documentManifestThirdTimePending';
                }
            });

            proceedToDownloadSelectionPage();

            cy.wait('@searchDocumentReferences');

            cy.getByTestId('toggle-selection-btn').click();
            cy.getByTestId('download-selected-files-btn').click();

            cy.wait('@documentManifestThirdTimePending');

            cy.title().should('have.string', 'Service error');
            cy.url().should('have.string', '/server-error?encodedError=');
        });

        it(
            'No download option when no Lloyd George record exists for a patient as a GP ADMIN role',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);

                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 404,
                }).as('lloydGeorgeStitch');

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');

                cy.getByTestId('download-all-files-link').should('not.exist');
            },
        );

        it(
            'No download option exists when a Lloyd George record exists for the patient as a GP CLINICAL role',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_CLINICAL);

                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 200,
                    body: viewLloydGeorgePayload,
                }).as('lloydGeorgeStitch');

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');

                cy.getByTestId('download-all-files-link').should('not.exist');
            },
        );

        it.skip(
            'It displays an error when the document manifest API call fails as a GP CLINICAL role',
            { tags: 'regression' },
            () => {
                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 200,
                    body: viewLloydGeorgePayload,
                }).as('lloydGeorgeStitch');

                cy.intercept('GET', '/DocumentManifest*', {
                    statusCode: 500,
                }).as('documentManifest');

                beforeEachConfiguration(Roles.GP_CLINICAL);

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');

                cy.getByTestId('download-all-files-link').should('exist');
                cy.getByTestId('download-all-files-link').click();

                cy.wait('@documentManifest');

                // Assert
                cy.contains(
                    'appropriate error for when the document manifest API call fails',
                ).should('be.visible');
            },
        );
    });
});
