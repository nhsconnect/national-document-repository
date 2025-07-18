import { Roles } from '../../support/roles';
import { routes } from '../../support/routes';

describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');

    const startUrl = '/';

    beforeEach(() => {
        cy.visit(baseUrl + startUrl);
    });

    it('should visit expected URL', { tags: 'regression' }, () => {
        cy.url().should('eq', baseUrl + startUrl);
        cy.title().should(
            'eq',
            'Access and store digital patient documents - Access and store digital patient documents',
        );
    });

    it('displays correct page title on home page', { tags: 'regression' }, () => {
        cy.get('.app-homepage-content h1').should(
            'have.text',
            'Access and store digital patient documents',
        );
    });

    it('displays start now button on home page', { tags: 'regression' }, () => {
        cy.get('.nhsuk-button').should('have.text', 'Start now');
    });

    it('displays service banner', { tags: 'regression' }, () => {
        cy.get('.nhsuk-phase-banner__content__tag').should('have.text', 'New service');
        cy.get('.nhsuk-phase-banner__text').should(
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
                    'Access and store digital patient documents',
                );
                cy.get('.nhsuk-navigation-container').should('not.exist');
                cy.get('.nhsuk-header__navigation-list').should('not.exist');

                cy.login(Roles.GP_CLINICAL);

                cy.url().should('eq', baseUrl + routes.home);
                cy.get('.nhsuk-navigation-container').should('exist');
                cy.get('.nhsuk-header__navigation-list').should('exist');
            },
        );

        const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

        gpRoles.forEach((role) => {
            it(
                `should display home page when user is ${Roles[role]} role in area`,
                { tags: 'regression' },
                () => {
                    cy.login(role);

                    cy.url().should('eq', baseUrl + routes.home);

                    cy.get('.nhsuk-navigation-container').should('exist');
                    cy.get('.nhsuk-header__navigation-list').should('exist');
                },
            );
        });

        it('should display home page when user is PCSE Role', { tags: 'regression' }, () => {
            cy.login(Roles.PCSE);

            cy.url().should('eq', baseUrl + routes.home);

            cy.get('.nhsuk-navigation-container').should('exist');
            cy.get('.nhsuk-header__navigation-list').should('exist');
        });
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
                    'Access and store digital patient documents',
                );
                cy.get('.nhsuk-header__navigation').should('not.exist');
                cy.get('.nhsuk-header__navigation-list').should('not.exist');

                cy.login(Roles.GP_CLINICAL);

                cy.get('.nhsuk-navigation-container').should('exist');
                cy.get('.nhsuk-header__navigation-list').should('exist');

                cy.intercept('GET', '/Auth/Logout', {
                    statusCode: 200,
                }).as('logout');

                cy.getByTestId('logout-btn').should('exist');
                cy.getByTestId('logout-btn').click();

                cy.wait('@logout');
                cy.url({ timeout: 10000 }).should('eq', baseUrl + startUrl);

                cy.get('.nhsuk-header__navigation').should('not.exist');
                cy.get('.nhsuk-header__navigation-list').should('not.exist');
            },
        );
    });
});
