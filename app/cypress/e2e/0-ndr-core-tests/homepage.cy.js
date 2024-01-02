const { Roles } = require('../../support/roles');

describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const homeUrl = '/';
    const searchUrl = '/search/upload';

    beforeEach(() => {
        cy.visit(homeUrl);
    });
    it('should visit expected URL', { tags: 'regression' }, () => {
        cy.url().should('eq', baseUrl + homeUrl);
    });

    it('displays correct page title on home page', { tags: 'regression' }, () => {
        cy.get('.app-homepage-content h1').should(
            'have.text',
            'Access and store digital GP records',
        );
    });

    it('displays start now button on home page', { tags: 'regression' }, () => {
        cy.get('.nhsuk-button').should('have.text', 'Start now');
    });

    it('displays service banner', { tags: 'regression' }, () => {
        cy.get('.govuk-phase-banner__content__tag').should('have.text', 'New Service');
        cy.get('.govuk-phase-banner__text').should(
            'have.text',
            'Your feedback will help us to improve this service.',
        );
    });

    context('Login tests', () => {
        it(
            'should display patient search page with navigation after user log in from homepage',
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

                cy.url().should('eq', baseUrl + searchUrl);
                cy.get('.nhsuk-header__navigation').should('exist');
                cy.get('.nhsuk-header__navigation-list').should('exist');
            },
        );
    });

    context('Logout tests', () => {
        it(
            'should display home page with no navigation after user log out',
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

                cy.url().should('eq', baseUrl + searchUrl);
                cy.get('.nhsuk-header__navigation').should('exist');
                cy.get('.nhsuk-header__navigation-list').should('exist');

                cy.getByTestId('logout-btn').should('exist');
                cy.getByTestId('logout-btn').click();
                cy.url({ timeout: 10000 }).should('contain', baseUrl + homeUrl);

                cy.get('.nhsuk-header__navigation').should('not.exist');
                cy.get('.nhsuk-header__navigation-list').should('not.exist');
            },
        );
    });
});
