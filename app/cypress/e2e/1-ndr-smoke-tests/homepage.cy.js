describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    context('Logged in tests', () => {
        beforeEach(() => {
            cy.visit(baseUrl);
        });

        it('[Smoke] displays expected page header on home page when logged in', () => {
            //ensure the page header is visable
            cy.get('header').should('have.length', 1);

            cy.get('.nhsuk-logo__background').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name--link').should(
                'have.text',
                'Access and store digital GP records',
            );

            cy.get('.nhsuk-header__navigation').should('have.length', 1);
            cy.get('.nhsuk-header__navigation-list').should('have.length', 1);
        });
    });
});
