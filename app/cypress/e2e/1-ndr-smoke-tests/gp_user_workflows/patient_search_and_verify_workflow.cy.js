import { Roles, roleName } from '../../../support/roles';

describe('GP Workflow: Patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.config('baseUrl');
    const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

    const workspace = Cypress.env('WORKSPACE');
    const activePatient = workspace === 'ndr-dev' ? '9730153817' : '9449305552';

    gpRoles.forEach((role) => {
        it(
            `[Smoke] Shows the Lloyd george view page when upload patient is verified and active as a ${roleName(
                role,
            )} `,
            { tags: 'smoke' },
            () => {
                cy.smokeLogin(role);
                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(activePatient);
                cy.get('#search-submit').click();

                cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/upload/result');
                cy.get('#verify-submit').click();

                cy.url({ timeout: 10000 }).should(
                    'eq',
                    baseUrl + '/search/patient/lloyd-george-record',
                );
            },
        );
    });
});
