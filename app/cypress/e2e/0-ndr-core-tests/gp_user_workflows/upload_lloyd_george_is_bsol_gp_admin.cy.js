import { Roles } from '../../../support/roles';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatient.json';

const baseUrl = Cypress.config('baseUrl');
const searchPatientUrl = '/search/patient';

describe('GP Workflow: Upload Lloyd George record when user is GP amin and patient has no record', () => {
    const beforeEachConfiguration = () => {
        cy.login(Roles.GP_ADMIN);
        cy.visit(searchPatientUrl);

        cy.intercept('GET', '/SearchPatient*', {
            statusCode: 200,
            body: searchPatientPayload,
        }).as('search');
        cy.intercept('GET', '/LloydGeorgeStitch*', {
            statusCode: 404,
        }).as('stitch');

        cy.getByTestId('nhs-number-input').type(searchPatientPayload.nhsNumber);
        cy.getByTestId('search-submit-btn').click();
        cy.wait('@search');
        cy.get('#verify-submit').click();
        cy.wait('@stitch');
        cy.getByTestId('upload-patient-record-button').click();
    };

    beforeEach(() => {
        beforeEachConfiguration();
    });

    context('Upload Lloyd George document', () => {
        it(
            `GP ADMIN user can upload Lloyd George files for an active patient with no existing record`,
            { tags: 'regression' },
            () => {
                cy.url().should('include', 'upload');
                cy.url().should('eq', baseUrl + '/patient/upload/lloyd-george-record');
            },
        );
    });
});
