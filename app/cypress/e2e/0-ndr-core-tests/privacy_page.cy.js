const { Roles } = require('../../support/roles');

describe('Privacy Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const startUrl = '/';
    const privacypolicyUrl = '/privacy-policy';
    const rolesToTest = [Roles.GP_ADMIN, Roles.GP_CLINICAL, Roles.PCSE];

    const loginAndVisitPrivacyPolicyPage = (role) => {
        cy.login(role);
        cy.visit(privacypolicyUrl);
    };

    it('verify privacy policy link in start up page', { tags: 'regression' }, () => {
        cy.visit(startUrl);
        cy.url().should('eq', baseUrl + startUrl);
        cy.get('.nhsuk-footer__list-item-link')
            .should('exist')
            .and('have.attr', { target: '_blank' });
        cy.getByTestId('privacy-link').invoke('removeAttr', 'target').click();
        cy.url().should('eq', baseUrl + privacypolicyUrl);
        cy.title().should('eq', 'Privacy notice - Access and store digital patient documents');
    });

    rolesToTest.forEach((role) => {
        const nameOfRole = Roles[role];
        describe(`Role: ${nameOfRole}`, () => {
            it(
                'Opens the privacy-policy page when a user clicks the privacy policy link at the footer',
                { tags: 'regression' },
                () => {
                    cy.login(role);

                    cy.get('.nhsuk-footer__list-item-link')
                        .should('exist')
                        .and('have.attr', { target: '_blank' });
                    cy.getByTestId('privacy-link')
                        // for test purpose, remove "target=_blank" as cypress not supporting multiple tabs
                        .invoke('removeAttr', 'target')
                        .click();
                    cy.url().should('eq', baseUrl + privacypolicyUrl);
                },
            );
            it('Should display the expected privacy policy details', { tags: 'regression' }, () => {
                loginAndVisitPrivacyPolicyPage(role);
                cy.get('.app-homepage-content h1', { timeout: 5000 }).should(
                    'have.text',
                    'Privacy notice',
                );
                cy.get('.app-homepage-content p', { timeout: 5000 }).should(
                    'include.text',
                    "If you use the 'Access and store digital patient documents' service using your",
                );
                cy.getByTestId('cis2-link', { timeout: 5000 })
                    .should('have.attr', 'href')
                    .and(
                        'include',
                        'https://am.nhsidentity.spineservices.nhs.uk/openam/XUI/?realm=/#/',
                    );
            });
        });
    });
});
