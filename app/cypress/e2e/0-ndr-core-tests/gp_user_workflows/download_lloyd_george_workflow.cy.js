import viewLloydGeorgePayload from '../../../fixtures/requests/GET_LloydGeorgeStitch.json';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatient.json';
import { Roles } from '../../../support/roles';
import { formatNhsNumber } from '../../../../src/helpers/utils/formatNhsNumber';

const baseUrl = Cypress.config('baseUrl');
const patientSearchUrl = '/patient/search';

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

    context('Download Lloyd George document', () => {
        it(
            'GP ADMIN user can download the Lloyd George document of an active patient',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);

                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 200,
                    body: viewLloydGeorgePayload,
                }).as('lloydGeorgeStitch');
                cy.title().should('eq', 'Verify patient details - Digital Lloyd George records');

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');
                cy.title().should('eq', 'Available records - Digital Lloyd George records');

                cy.intercept('GET', '/DocumentManifest*', {
                    statusCode: 200,
                    body: baseUrl + '/browserconfig.xml', // uses public served file in place of a ZIP file
                }).as('documentManifest');

                cy.getByTestId('download-all-files-link').should('exist');
                cy.getByTestId('download-all-files-link').click();
                cy.title().should('eq', 'Downloading documents - Digital Lloyd George records');

                cy.wait('@documentManifest');

                // Assert contents of page when downloading
                cy.contains('Downloading documents').should('be.visible');
                cy.contains(
                    `Preparing download for ${viewLloydGeorgePayload.number_of_files} files`,
                ).should('be.visible');
                cy.contains('Compressing record into a zip file').should('be.visible');
                cy.contains('Cancel').should('be.visible');

                // Assert contents of page after download
                cy.title().should('eq', 'Download complete - Digital Lloyd George records');

                cy.contains('Download complete').should('be.visible');
                cy.contains('You have successfully downloaded the Lloyd George record of:').should(
                    'be.visible',
                );
                cy.contains(
                    `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
                ).should('be.visible');
                cy.contains(
                    `NHS number: ${formatNhsNumber(searchPatientPayload.nhsNumber)}`,
                ).should('be.visible');

                // Assert file has been downloaded
                cy.readFile(`${Cypress.config('downloadsFolder')}/browserconfig.xml`);

                cy.getByTestId('return-btn').click();

                // Assert return button returns to pdf view
                cy.getByTestId('pdf-card').should('be.visible');
            },
        );

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
