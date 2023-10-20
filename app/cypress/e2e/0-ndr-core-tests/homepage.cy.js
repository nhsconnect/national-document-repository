describe('home page', () => {
    const baseUrl = 'http://localhost:3000/';

    context('logged in', () => {
        beforeEach(() => {
            cy.login('gp');
            cy.visit(baseUrl);
        });

        it('displays expected page header on home page when logged in', () => {
            //ensure the page header is visable
            cy.get('header').should('have.length', 1);

            cy.get('.nhsuk-logo__background').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name--link').should(
                'have.text',
                'Inactive Patient Record Administration',
            );

            cy.get('.nhsuk-header__navigation').should('have.length', 1);
            cy.get('.nhsuk-header__navigation-list').should('have.length', 1);
        });
    });

    context('logged out', () => {
        beforeEach(() => {
            cy.visit(baseUrl);
        });

        it('Test expected URL is correct', () => {
            cy.url().should('eq', 'http://localhost:3000/');
        });

        it('displays page header with no navigation on home page when logged out', () => {
            cy.get('header').should('have.length', 1);

            cy.get('.nhsuk-logo__background').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name--link').should(
                'have.text',
                'Inactive Patient Record Administration',
            );

            cy.get('.nhsuk-header__navigation').should('have.length', 0);
            cy.get('.nhsuk-header__navigation-list').should('have.length', 0);
        });

        it('displays correct page title on home page', () => {
            cy.get('.app-homepage-content h1').should(
                'have.text',
                'Inactive Patient Record Administration',
            );
        });

        it('displays start now button on home page', () => {
            cy.get('.nhsuk-button').should('have.text', 'Start now');
        });
    });
});
