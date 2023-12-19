describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const username = Cypress.env('USERNAME');
    const password = Cypress.env('PASSWORD');

    const homeUrl = '/';
    beforeEach(() => {
        cy.visit(homeUrl);
    });

    it('[Smoke] should visit expected URL', { tags: 'smoke' }, () => {
        cy.url().should('eq', baseUrl + homeUrl);
    });

    context('Login tests', () => {
        it('displays expected page header on home page when logged in', { tags: 'smoke' }, () => {
            // Add CIS2 login steps
            cy.get('header').should('have.length', 1);

            cy.get('.nhsuk-logo__background').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name--link').should(
                'have.text',
                'Access and store digital GP records',
            );

            cy.getByTestId('start-btn').should('exist');
            cy.getByTestId('start-btn').click();
            // Restore once login steps implemented
            // cy.get('.nhsuk-header__navigation').should('have.length', 1);
            // cy.get('.nhsuk-header__navigation-list').should('have.length', 1);
        });
    });
});
