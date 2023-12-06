describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    beforeEach(() => {
        cy.visit(baseUrl);
    });

    it('[Smoke] should visit expected URL', () => {
        cy.url().should('eq', baseUrl);
    });

    context('Login tests', () => {
        it('[Smoke] displays expected page header on home page when logged in', () => {
            // Add CIS2 login steps
            cy.get('header').should('have.length', 1);

            cy.get('.nhsuk-logo__background').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name--link').should(
                'have.text',
                'Access and store digital GP records',
            );

            // Restore once login steps implemented
            // cy.get('.nhsuk-header__navigation').should('have.length', 1);
            // cy.get('.nhsuk-header__navigation-list').should('have.length', 1);
        });
    });
});
