import { pdsPatients, stubPatients } from '../../../support/patients';
import { Roles } from '../../../support/roles';

const workspace = Cypress.env('WORKSPACE');
const activePatient =
    workspace === 'ndr-dev' ? pdsPatients.activeNoUploadBsol : stubPatients.activeNoUploadBsol;
describe('GP Workflow: Upload Lloyd George record', () => {
    context('Upload a Lloyd George document', () => {
        it('[Smoke] BSOL GP ADMIN can upload and then view a Lloyd George record for an active patient with no record', () => {
            cy.smokeLogin(Roles.GP_ADMIN);

            cy.getByTestId('search-patient-btn').click();

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(activePatient);
            cy.get('#search-submit').click();

            cy.url().should('contain', '/search/patient/verify');
            cy.get('#verify-submit').click();

            cy.url().should('contain', '/patient/view/lloyd-george-record');
            cy.getByTestId('upload-patient-record-text').should(
                'have.text',
                'You can upload full or part of a patient record',
            );
            cy.getByTestId('upload-patient-record-button').should('exist');
            cy.getByTestId('upload-patient-record-button').click();
        });
    });
});
