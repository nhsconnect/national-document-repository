const { Roles } = require('../../support/roles');

describe('Privacy Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const privacypolicyUrl = '/privacy-policy';
    const rolesToTest = [Roles.GP_ADMIN, Roles.GP_CLINICAL, Roles.PCSE];

    const loginAndVisitPrivacyPolicyPage = (role) => {
        cy.login(role);
        cy.visit(privacypolicyUrl);
    };

    rolesToTest.forEach((role) => {
        const nameOfRole = Roles[role];
        describe(`Role: ${nameOfRole}`, () => {
            it(
                'opens the privacy-policy page when a user clicks the link at the footer',
                { tags: 'regression' },
                () => {
                    cy.login(role);

                    cy.get('.nhsuk-footer__list-item-link')
                        .should('exist')
                        .and('have.attr', { target: '_blank' });
                    cy.get('.Privacy notice')
                        // for test purpose, remove "target=_blank" as cypress not supporting multiple tabs
                        .invoke('removeAttr', 'target')
                        .click();
                    cy.url().should('eq', baseUrl + privacypolicyUrl);
                },
            );
            it(
                'When should display the expectef privacy policy details',
                { tags: 'regression' },
                () => {
                    loginAndVisitPrivacyPolicyPage(role);
                    cy.get('.Privacy notice h1', { timeout: 5000 }).should(
                        'have.text',
                        'If you access the Lloyd George patient records digital service using your NHS Care Identity credentials, your NHS Care Identity credentials are managed by NHS England.',
                    );
                },
            );
        });
    });
});
