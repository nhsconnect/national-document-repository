import { pdsPatients, stubPatients } from '../../../support/patients';
import { Roles } from '../../../support/roles';
const uploadedFilePathNames = {
    LG: [
        'cypress/fixtures/lg-files/1of1_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        [
            'cypress/fixtures/lg-files/1of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
            'cypress/fixtures/lg-files/2of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        ],
    ],
};

const uploadedFileNames = {
    LG: [
        '1of1_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        [
            '1of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
            '2of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        ],
    ],
};

const workspace = Cypress.env('WORKSPACE');
const activePatient =
    workspace === 'ndr-dev' ? pdsPatients.activeNoUploadBsol : stubPatients.activeNoUploadBsol;
describe('GP Workflow: Upload Lloyd George record', () => {
    context('Upload a Lloyd George document', () => {
        it('[Smoke] BSOL GP ADMIN can upload and then view a Lloyd George record for an active patient with no record', () => {
            cy.smokeLogin(Roles.GP_ADMIN_BSOL);

            cy.get('#nhs-number-input').should('exist');
            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(activePatient);
            cy.getByTestId('search-submit-btn').should('exist');
            cy.getByTestId('search-submit-btn').click();

            cy.url().should('contain', '/search/patient/verify');

            cy.get('#verify-submit').should('exist');
            cy.get('#verify-submit').click();

            cy.url().should('contain', '/patient/view/lloyd-george-record');
            cy.getByTestId('upload-patient-record-text').should(
                'include.text',
                'You can upload full or part of a patient record',
            );
            cy.getByTestId('upload-patient-record-button').should('exist');
            cy.getByTestId('upload-patient-record-button').click();
            cy.getByTestId('button-input').selectFile(uploadedFilePathNames.LG[0], { force: true });
            cy.get('#upload-button').click();

            cy.getByTestId('upload-documents-table').should('contain', uploadedFileNames.LG[0]);
        });
    });
});
