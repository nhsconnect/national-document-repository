import { Roles, roleName } from '../../../support/roles';

describe('GP Workflow: Patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.config('baseUrl');
    const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

    const testNotFoundPatient = '1000000001';
    const activePatient = '9449305552';
    const inactivePatient = '9449305552';

    gpRoles.forEach((role) => {
        beforeEach(() => {
            cy.smokeLogin(role);
        });

        it(
            `[Smoke] Shows patient upload screen when patient search is used by as a
               ${roleName(role)} and patient response is inactive`,
            { tags: 'smoke' },
            () => {
                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(inactivePatient);

                cy.get('#search-submit').click();

                cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/upload/result');
                cy.get('#gp-message').should('be.visible');
                cy.get('#gp-message').should(
                    'have.text',
                    'Ensure these patient details match the records and attachments that you upload',
                );
                cy.get('#verify-submit').click();

                cy.url().should('include', 'submit');
                cy.url().should('eq', baseUrl + '/upload/submit');
            },
        );

        it.only(
            `[Smoke] Does not show verify patient view when the search finds no patient as ${roleName(
                role,
            )}`,
            { tags: 'smoke' },
            () => {
                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(testNotFoundPatient);

                cy.get('#search-submit').click();

                cy.get('#nhs-number-input--error-message').should('be.visible');
                cy.get('#nhs-number-input--error-message').should(
                    'have.text',
                    'Error: Sorry, patient data not found.',
                );
                cy.get('#error-box-summary').should('be.visible');
                cy.get('#error-box-summary').should('have.text', 'There is a problem');
            },
        );

        it(
            `[Smoke] Shows the upload documents page when upload patient is verified and inactive as a ${roleName(
                role,
            )} `,
            { tags: 'smoke' },
            () => {
                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(inactivePatient);
                cy.get('#search-submit').click();

                cy.get('#verify-submit').click();

                cy.url().should('include', 'submit');
                cy.url().should('eq', baseUrl + '/upload/submit');
            },
        );

        it(
            `[Smoke] Shows the Lloyd george view page when upload patient is verified and active as a ${roleName(
                role,
            )} `,
            { tags: 'smoke' },
            () => {
                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(activePatient);
                cy.get('#search-submit').click();

                cy.get('#verify-submit').click();

                cy.url().should('include', 'lloyd-george-record');
                cy.url().should('eq', baseUrl + '/search/patient/lloyd-george-record');
            },
        );
    });
});
