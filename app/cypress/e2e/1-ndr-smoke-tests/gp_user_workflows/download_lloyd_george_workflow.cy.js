import { pdsPatients } from '../../../support/patients';
import { Roles } from '../../../support/roles';

const baseUrl = Cypress.config('baseUrl');

describe('GP Workflow: View Lloyd George record', () => {
    context('Download Lloyd George document', () => {
        it(
            '[Smoke] GP ADMIN user can download the Lloyd George document of an active patient',
            { tags: 'smoke' },
            () => {
                cy.smokeLogin(Roles.GP_ADMIN);
                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(pdsPatients.activeUpload);
                cy.get('#search-submit').click();

                cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/upload/result');
                cy.get('#verify-submit').click();

                cy.url({ timeout: 10000 }).should(
                    'eq',
                    baseUrl + '/search/patient/lloyd-george-record',
                );
                // cy.get('#verify-submit').click();
                // cy.wait('@lloydGeorgeStitch');

                // cy.intercept('GET', '/DocumentManifest*', {
                //     statusCode: 200,
                //     body: baseUrl + '/browserconfig.xml', // uses public served file in place of a ZIP file
                // }).as('documentManifest');

                // cy.getByTestId('actions-menu').click();
                // cy.getByTestId('download-all-files-link').click();

                // cy.wait('@documentManifest');

                // // Assert contents of page when downloading
                // cy.contains('Downloading documents').should('be.visible');
                // cy.contains(
                //     `Preparing download for ${viewLloydGeorgePayload.number_of_files} files`,
                // ).should('be.visible');
                // cy.contains('Compressing record into a zip file').should('be.visible');
                // cy.contains('Cancel').should('be.visible');

                // // Assert contents of page after download
                // cy.contains('Download complete').should('be.visible');
                // cy.contains('Documents from the Lloyd George record of:').should('be.visible');
                // cy.contains(
                //     `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
                // ).should('be.visible');
                // cy.contains(`(NHS number: ${searchPatientPayload.nhsNumber})`).should('be.visible');

                // // Assert file has been downloaded
                // cy.readFile(`${Cypress.config('downloadsFolder')}/browserconfig.xml`);

                // cy.getByTestId('return-btn').click();

                // // Assert return button returns to pdf view
                // cy.getByTestId('pdf-card').should('be.visible');
            },
        );

        // it(
        //     'No download option or menu exists when no Lloyd George record exists for a patient as a GP ADMIN role',
        //     { tags: 'regression' },
        //     () => {
        //         beforeEachConfiguration(Roles.GP_ADMIN);

        //         cy.intercept('GET', '/LloydGeorgeStitch*', {
        //             statusCode: 404,
        //         }).as('lloydGeorgeStitch');

        //         cy.get('#verify-submit').click();
        //         cy.wait('@lloydGeorgeStitch');

        //         cy.getByTestId('actions-menu').should('not.exist');
        //     },
        // );

        // it(
        //     'No download option exists when a Lloyd George record exists for the patient as a GP CLINICAL role',
        //     { tags: 'regression' },
        //     () => {
        //         beforeEachConfiguration(Roles.GP_CLINICAL);

        //         cy.intercept('GET', '/LloydGeorgeStitch*', {
        //             statusCode: 200,
        //             body: viewLloydGeorgePayload,
        //         }).as('lloydGeorgeStitch');

        //         cy.get('#verify-submit').click();
        //         cy.wait('@lloydGeorgeStitch');

        //         cy.getByTestId('actions-menu').click();
        //         cy.getByTestId('download-all-files-link').should('not.exist');
        //     },
        // );

        // it.skip(
        //     'It displays an error when the document manifest API call fails as a GP CLINICAL role',
        //     { tags: 'regression' },
        //     () => {
        //         cy.intercept('GET', '/LloydGeorgeStitch*', {
        //             statusCode: 200,
        //             body: viewLloydGeorgePayload,
        //         }).as('lloydGeorgeStitch');

        //         cy.intercept('GET', '/DocumentManifest*', {
        //             statusCode: 500,
        //         }).as('documentManifest');

        //         cy.get('#verify-submit').click();
        //         cy.wait('@lloydGeorgeStitch');

        //         cy.getByTestId('actions-menu').click();
        //         cy.getByTestId('download-all-files-link').click();

        //         cy.wait('@documentManifest');

        //         // Assert
        //         cy.contains(
        //             'appropriate error for when the document manifest API call fails',
        //         ).should('be.visible');
        //     },
        // );
    });
});
