import { pdsPatients, stubPatients } from '../../../support/patients';
import { Roles, roleName } from '../../../support/roles';

describe('GP Workflow: Patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.config('baseUrl');
    const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

    const workspace = Cypress.env('WORKSPACE');
    const activePatient =
        workspace === 'ndr-dev' ? pdsPatients.activeUpload : stubPatients.activeUpload;
    const homeUrl = '/home';
    const patientVerifyUrl = '/patient/verify';
    const lloydGeorgeRecordUrl = '/patient/lloyd-george-record';

    gpRoles.forEach((role) => {
        it(
            `[Smoke] Shows the Lloyd george view page when patient is verified and active as a ${roleName(
                role,
            )} `,
            { tags: 'smoke' },
            () => {
                cy.smokeLogin(role);

                cy.url({ timeout: 10000 }).should('eq', baseUrl + homeUrl);
                cy.getByTestId('search-patient-btn').should('exist');
                cy.getByTestId('search-patient-btn').click();

                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(activePatient);
                cy.get('#search-submit').click();

                cy.url({ timeout: 20000 }).should('eq', baseUrl + patientVerifyUrl);
                cy.get('#verify-submit').click();

                cy.url({ timeout: 10000 }).should('eq', baseUrl + lloydGeorgeRecordUrl);
            },
        );
    });
});
