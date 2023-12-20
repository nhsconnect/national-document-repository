const { Roles } = require('../../support/roles');

describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const homeUrl = '/';

    beforeEach(() => {
        cy.visit(homeUrl);
    });
    it('should visit expected URL', { tags: 'regression' }, () => {
        cy.url().should('eq', baseUrl + homeUrl);
    });

    context('Login tests', () => {
        it(
            'should display patient search page with navigation after user log in',
            { tags: 'regression' },
            () => {
                cy.get('header').should('exist');

                cy.get('.nhsuk-logo__background').should('exist');
                cy.get('.nhsuk-header__transactional-service-name').should('exist');
                cy.get('.nhsuk-header__transactional-service-name')
                    .children()
                    .should('have.length', 1);
                cy.get('.nhsuk-header__transactional-service-name--link').should('exist');
                cy.get('.nhsuk-header__transactional-service-name--link').should(
                    'have.text',
                    'Access and store digital GP records',
                );
                cy.get('.nhsuk-header__navigation').should('not.exist');
                cy.get('.nhsuk-header__navigation-list').should('not.exist');

                cy.login(Roles.GP_CLINICAL);

                cy.get('.nhsuk-header__navigation').should('exist');
                cy.get('.nhsuk-header__navigation-list').should('exist');
            },
        );
    });

    context('Logout tests', () => {
        // TODO: Align with smoke logout test
        it(
            'should display home page with no navigation after user log out',
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
