import viewLloydGeorgePayload from '../../fixtures/requests/GET_LloydGeorgeStitch.json';
import searchPatientPayload from '../../fixtures/requests/GET_SearchPatient.json';

const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';

describe('GP View Lloyd George Workflow', () => {
    beforeEach(() => {
        // Arrange
        cy.login('GP_ADMIN');


        // search patient
        cy.intercept('GET', '/SearchPatient*', {
            statusCode: 200,
            body: searchPatientPayload,
        }).as('search');
        cy.get('#nhs-number-input').type(searchPatientPayload.nhsNumber);
        cy.get('#search-submit').click();
        cy.wait('@search');

        // verify patient is active
        cy.get('#active-radio-button').click();
    });

    context('View Lloyd George document', () => {
        it('allows a GP user to view the Lloyd George document of an active patient', () => {
            cy.intercept('GET', '/LloydGeorgeStitch*', {
                statusCode: 200,
                body: viewLloydGeorgePayload,
            }).as('lloydGeorgeStitch');

            cy.get('#verify-submit').click();
            cy.wait('@lloydGeorgeStitch');

            // Assert
            assertPatientInfo();
            cy.getByTestId('pdf-card')
                .should('include.text', 'Lloyd George record')
                .should('include.text', 'Last updated: 09 October 2023 at 15:41:38')
                .should('include.text', '12 files | File size: 502 KB | File format: PDF');
            cy.getByTestId('pdf-viewer').should('be.visible');

            // Act - open full screen view
            cy.getByTestId('full-screen-btn').click();

            // Assert
            assertPatientInfo();
            cy.getByTestId('pdf-card').should('not.exist');
            cy.getByTestId('pdf-viewer').should('be.visible');

            //  Act - close full screen view
            cy.getByTestId('back-link').click();

            // Assert
            cy.getByTestId('pdf-card').should('be.visible');
            cy.getByTestId('pdf-viewer').should('be.visible');
        });

        it('displays an empty Lloyd George card when no Lloyd George record exists for the patient', () => {
            cy.intercept('GET', '/LloydGeorgeStitch*', {
                statusCode: 404,
            });
            cy.get('#verify-submit').click();

            // Assert
            assertPatientInfo();
            assertEmptyLloydGeorgeCard();
        });

        it('displays an empty Lloyd George card when the backend API call fails', () => {
            cy.intercept('GET', '/LloydGeorgeStitch*', {
                statusCode: 500,
            });
            cy.get('#verify-submit').click();

            //Assert
            assertPatientInfo();
            assertEmptyLloydGeorgeCard();
        });
    });

    context('Download Lloyd George document', () => {
        beforeEach(() => {
            cy.intercept('GET', '/LloydGeorgeStitch*', {
                statusCode: 200,
                body: viewLloydGeorgePayload,
            }).as('lloydGeorgeStitch');
            cy.get('#verify-submit').click();
            cy.wait('@lloydGeorgeStitch');
        });

        it('allows a GP user to download the Lloyd George document of an active patient', () => {
            cy.intercept('GET', '/DocumentManifest*', {
                statusCode: 200,
                body: baseUrl + 'browserconfig.xml', // uses public served file in place of a ZIP file
            }).as('documentManifest');

            cy.getByTestId('actions-menu').click();
            cy.getByTestId('download-all-files-link').click();

            cy.wait('@documentManifest');

            // Assert contents of page when downloading
            cy.contains('Downloading documents').should('be.visible');
            cy.contains(
                `Preparing download for ${viewLloydGeorgePayload.number_of_files} files`,
            ).should('be.visible');
            cy.contains('Compressing record into a zip file').should('be.visible');
            cy.contains('Cancel').should('be.visible');

            // Assert contents of page after download
            cy.contains('Download complete').should('be.visible');
            cy.contains('Documents from the Lloyd George record of:').should('be.visible');
            cy.contains(
                `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
            ).should('be.visible');
            cy.contains(`(NHS number: ${searchPatientPayload.nhsNumber})`).should('be.visible');

            // Assert file has been downloaded
            cy.readFile(`${Cypress.config('downloadsFolder')}/browserconfig.xml`);

            cy.getByTestId('return-btn').click();

            // Assert return button returns to pdf view
            cy.getByTestId('pdf-card').should('be.visible');
        });

        // TODO - PRMDR-401 - implement error scenario in UI and amend assertions accordingly
        it.skip('displays an error when no Lloyd George record exists for the patient', () => {
            cy.intercept('GET', '/DocumentManifest*', {
                statusCode: 204,
                body: 'No documents found for given NHS number and document type',
            }).as('documentManifest');

            cy.getByTestId('actions-menu').click();
            cy.getByTestId('download-all-files-link').click();

            cy.wait('@documentManifest');

            // Assert
            cy.contains('appropriate error for when Lloyd George document cannot be found').should(
                'be.visible',
            );
        });

        // TODO - PRMDR-401 - implement error scenario in UI and amend assertions accordingly
        it.skip('displays an error when the document manifest backend API call fails', () => {
            cy.intercept('GET', '/DocumentManifest*', {
                statusCode: 500,
            }).as('documentManifest');

            cy.getByTestId('actions-menu').click();
            cy.getByTestId('download-all-files-link').click();

            cy.wait('@documentManifest');

            // Assert
            cy.contains(
                'appropriate error for when the document manifest backend API call fails',
            ).should('be.visible');
        });
    });

    const assertPatientInfo = () => {
        cy.getByTestId('patient-name').should(
            'have.text',
            `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
        );
        cy.getByTestId('patient-nhs-number').should('have.text', `NHS number: 900 000 0009`);
        cy.getByTestId('patient-dob').should('have.text', `Date of birth: 01 January 1970`);
    };

    const assertEmptyLloydGeorgeCard = () => {
        cy.getByTestId('pdf-card').should('include.text', 'Lloyd George record');
        cy.getByTestId('pdf-card').should('include.text', 'No documents are available');
    };
});
