import { pdsPatients, stubPatients } from '../../../support/patients';
import { Roles } from '../../../support/roles';

const workspace = Cypress.env('WORKSPACE');
const uploadedFilePathNames = [
    'cypress/fixtures/lg-files/jane_smith/1of3_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010].pdf',
    'cypress/fixtures/lg-files/jane_smith/2of3_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010].pdf',
    'cypress/fixtures/lg-files/jane_smith/3of3_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010].pdf',
];
const uploadedFileNames = [
    '1of3_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010].pdf',
    '2of3_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010].pdf',
    '3of3_Lloyd_George_Record_[Jane Smith]_[9000000004]_[22-10-2010].pdf',
];
const viewLloydGeorgeRecordUrl = '/patient/view/lloyd-george-record';
const baseUrl = Cypress.config('baseUrl');
const tableName = `${workspace}_LloydGeorgeReferenceMetadata`;

const activePatient =
    workspace === 'ndr-dev' ? pdsPatients.activeNoUploadBsol : stubPatients.activeNoUploadBsol;

describe('GP Workflow: Upload Lloyd George record', () => {
    context('Upload a Lloyd George document', () => {
        beforeEach(() => {
            // cy.getItemFromDynamoDb(tableName, uploadedFileNames[0]);
        });
        afterEach(() => {
            // cy.deleteDocRefFromDynamoDb(tableName, uploadedFileNames[0]);
        });

        it(
            '[Smoke] BSOL GP ADMIN can upload and then view a Lloyd George record for an active patient with no record',
            { tags: 'smoke', defaultCommandTimeout: 20000 },
            () => {
                cy.smokeLogin(Roles.GP_ADMIN_BSOL);

                cy.get('#nhs-number-input').should('exist');
                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(activePatient);
                cy.getByTestId('search-submit-btn').should('exist');
                cy.getByTestId('search-submit-btn').click();

                cy.url({ timeout: 15000 }).should('contain', '/search/patient/verify');

                cy.get('#verify-submit').should('exist');
                cy.get('#verify-submit').click();

                cy.url().should('contain', '/patient/view/lloyd-george-record');
                cy.getByTestId('upload-patient-record-text').should(
                    'include.text',
                    'You can upload full or part of a patient record',
                );
                cy.getByTestId('upload-patient-record-button').should('exist');
                cy.getByTestId('upload-patient-record-button').click();
                uploadedFilePathNames.forEach((file) => {
                    cy.getByTestId('button-input').selectFile(file, { force: true });
                });
                cy.get('#upload-button').click();
                uploadedFileNames.forEach((name) => {
                    cy.getByTestId('upload-documents-table').should('contain', name);
                });
                uploadedFileNames.forEach((name) => {
                    cy.getByTestId('upload-documents-table').should('contain', name);
                });

                cy.getByTestId('upload-complete-page', { timeout: 20000 }).should('exist');
                cy.getByTestId('upload-complete-page')
                    .should('include.text', 'Record uploaded for')
                    .should(
                        'include.text',
                        `You have successfully uploaded ${uploadedFileNames.length} files`,
                    )
                    .should('include.text', 'Hide files');

                uploadedFileNames.forEach((name) => {
                    cy.getByTestId('upload-complete-page').should('contain', name);
                    cy.getByTestId(name.split('_')[0])
                        .invoke('attr', 'data-ref')
                        .then((ref) => {
                            cy.deleteItemFromDynamoDb(tableName, ref);
                        });
                });
                cy.getByTestId('upload-complete-card').should('be.visible');
                cy.getByTestId('view-record-btn').should('be.visible');
                cy.getByTestId('search-patient-btn').should('be.visible');
                cy.getByTestId('view-record-btn').should('be.visible');
                cy.getByTestId('view-record-btn').click();
                cy.url().should('eq', baseUrl + viewLloydGeorgeRecordUrl);
            },
        );
    });
});
