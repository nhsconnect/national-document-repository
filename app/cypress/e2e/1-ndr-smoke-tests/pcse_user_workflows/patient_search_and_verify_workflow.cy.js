const { Roles } = require('../../../support/roles');

describe('PCSE Workflow: patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.config('baseUrl');
    const homeUrl = '/';

    beforeEach(() => {
        cy.visit(homeUrl);
    });

    it(
        '[Smoke] It redirects to the patient download screen when patient search successfully by a PCSE user',
        { tags: 'smoke' },
        () => {
            const activePatient = '9449305552';
            cy.smokeLogin(Roles.PCSE);
            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(activePatient);

            cy.get('#search-submit').click();
            cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/patient/result');
            cy.get('#gp-message').should('not.exist');

            cy.get('#verify-submit').click();
            cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/results');
        },
    );

    it(
        '[Smoke] It searches for a valid patient successfully when the user enters a known nhs number with spaces by a PCSE user',
        { tags: 'smoke' },
        () => {
            const activePatient = '944 930 5552';
            cy.smokeLogin(Roles.PCSE);
            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(activePatient);

            cy.get('#search-submit').click();
            cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/patient/result');
            cy.get('#gp-message').should('not.exist');

            cy.get('#verify-submit').click();
            cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/results');
        },
    );

    it(
        '[Smoke] It searches for a valid patient successfully when the user enters a known nhs number with dashes by a PCSE user',
        { tags: 'smoke' },
        () => {
            const activePatient = '944-930-5552';

            cy.smokeLogin(Roles.PCSE);
            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(activePatient);

            cy.get('#search-submit').click();
            cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/patient/result');
            cy.get('#gp-message').should('not.exist');

            cy.get('#verify-submit').click();
            cy.url({ timeout: 10000 }).should('eq', baseUrl + '/search/results');
        },
    );
});
