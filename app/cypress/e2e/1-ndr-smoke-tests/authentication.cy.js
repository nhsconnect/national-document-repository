const { Roles } = require('../../support/roles');

describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const homeUrl = '/';

    it('[Smoke] should visit expected URL', { tags: 'smoke' }, () => {
        cy.visit(homeUrl);
        cy.url().should('eq', baseUrl + homeUrl);
    });

    it(
        '[Smoke] should display patient search page with navigation after user log in',
        { tags: 'smoke' },
        () => {
            cy.get('header').should('exist');

            cy.get('.nhsuk-logo__background').should('exist');
            cy.get('.nhsuk-header__transactional-service-name').should('exist');
            cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name--link').should('exist');
            cy.get('.nhsuk-header__transactional-service-name--link').should(
                'have.text',
                'Access and store digital GP records',
            );
            cy.get('.nhsuk-header__navigation').should('not.exist');
            cy.get('.nhsuk-header__navigation-list').should('not.exist');

            cy.smokeLogin(Roles.GP_CLINICAL);

            cy.get('.nhsuk-header__navigation').should('exist');
            cy.get('.nhsuk-header__navigation-list').should('exist');
        },
    );
});
