describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const homeUrl = '/';

    beforeEach(() => {
        cy.visit(baseUrl);
    });
    it('should visit expected URL', { tags: 'regression' }, () => {
        cy.url().should('eq', baseUrl + homeUrl);
    });

    context('Login tests', () => {
        beforeEach(() => {
            cy.login('GP_ADMIN');
        });

        it(
            'displays expected page header on home page when logged in',
            { tags: 'regression' },
            () => {
                //ensure the page header is visable
                cy.get('header').should('have.length', 1);

                cy.get('.nhsuk-logo__background').should('have.length', 1);
                cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
                cy.get('.nhsuk-header__transactional-service-name')
                    .children()
                    .should('have.length', 1);
                cy.get('.nhsuk-header__transactional-service-name--link').should(
                    'have.text',
                    'Access and store digital GP records',
                );

                cy.get('.nhsuk-header__navigation').should('have.length', 1);
                cy.get('.nhsuk-header__navigation-list').should('have.length', 1);
            },
        );
    });

    context('Logout tests', () => {
        beforeEach(() => {
            cy.visit(baseUrl);
        });

        it(
            'displays page header with no navigation on home page when logged out',
            { tags: 'regression' },
            () => {
                cy.get('header').should('have.length', 1);

                cy.get('.nhsuk-logo__background').should('have.length', 1);
                cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
                cy.get('.nhsuk-header__transactional-service-name')
                    .children()
                    .should('have.length', 1);
                cy.get('.nhsuk-header__transactional-service-name--link').should(
                    'have.text',
                    'Access and store digital GP records',
                );

                cy.get('.nhsuk-header__navigation').should('have.length', 0);
                cy.get('.nhsuk-header__navigation-list').should('have.length', 0);
            },
        );

        it('displays correct page title on home page', { tags: 'regression' }, () => {
            cy.get('.app-homepage-content h1').should(
                'have.text',
                'Access and store digital GP records',
            );
        });

        it('displays start now button on home page', { tags: 'regression' }, () => {
            cy.get('.nhsuk-button').should('have.text', 'Start now');
        });
    });
});
