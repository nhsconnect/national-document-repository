import { pdsPatients } from '../../../support/patients';
import { Roles } from '../../../support/roles';
import { dbItem } from '../../../fixtures/dynamo-db-items/active-patient.json';

const workspace = Cypress.env('WORKSPACE');
dbItem.FileLocation = dbItem.FileLocation.replace('{env}', workspace);
const activePatient = pdsPatients.activeUpload;
const bucketName = `${workspace}-lloyd-george-store`;
const tableName = `${workspace}_LloydGeorgeReferenceMetadata`;
const fileName = `${activePatient}/e4a6d7f7-01f3-44be-8964-515b2c0ec180`;

describe('GP Workflow: View Lloyd George record', () => {
    context('Download Lloyd George document', () => {
        before(() => {
            cy.deleteFileFromS3(bucketName, fileName);
            cy.deleteItemFromDynamoDb(tableName, dbItem.ID);
            cy.addFileToS3(bucketName, fileName, '../../../fixtures/test_patient_record.pdf');
            cy.addItemToDynamoDb(tableName, dbItem);
        });

        after(() => {
            cy.deleteFileFromS3(bucketName, fileName);
            cy.deleteItemFromDynamoDb(tableName, dbItem.ID);
        });

        it(
            '[Smoke] GP ADMIN user can download the Lloyd George document of an active patient',
            { tags: 'smoke' },
            () => {
                cy.smokeLogin(Roles.GP_ADMIN);

                cy.getByTestId('search-patient-btn').click();

                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(activePatient);
                cy.get('#search-submit').click();

                cy.url({ timeout: 10000 }).should('contain', '/search/patient/verify');
                cy.get('#verify-submit').click();

                cy.url({ timeout: 10000 }).should('contain', '/patient/view/lloyd-george-record');

                cy.getByTestId('actions-menu').click();
                cy.getByTestId('download-all-files-link').click();

                // Assert contents of page when downloading
                cy.contains('Downloading documents').should('be.visible');
                cy.contains('Preparing download for').should('be.visible');
                cy.contains('Compressing record into a zip file').should('be.visible');
                cy.contains('Cancel').should('be.visible');

                // Assert contents of page after download
                cy.contains('Download complete').should('be.visible');
                cy.contains('Documents from the Lloyd George record of:').should('be.visible');
                cy.contains(`(NHS number: ${activePatient})`).should('be.visible');

                // Assert file has been downloaded
                cy.readFile(`${Cypress.config('downloadsFolder')}/patient-record-${activePatient}`);
            },
        );
    });
});
