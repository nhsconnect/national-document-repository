const { Roles } = require('../../support/roles');

describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');

    const startUrl = '/';
    const homeUrl = '/home';
    const patientSearchUrl = '/patient/search';
    const patientVerifyUrl = '/patient/verify';
    const lloydGeorgeViewUrl = '/patient/lloyd-george-record/';
    const arfDownloadUrl = '/patient/download';

    beforeEach(() => {
        cy.visit(baseUrl + startUrl);
    });

    it('should visit expected URL', { tags: 'regression' }, () => {
        cy.url().should('eq', baseUrl + startUrl);
        cy.title().should(
            'eq',
            'Access and store digital GP records - Digital Lloyd George records',
        );
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

                cy.login(Roles.GP_CLINICAL, true);

                cy.url().should('eq', baseUrl + patientSearchUrl);
                cy.get('.nhsuk-header__navigation').should('exist');
                cy.get('.nhsuk-header__navigation-list').should('exist');
            },
        );

        const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];
        gpRoles.forEach((role) => {
            it(
                `should display non-BSOL landing page when user is ${Roles[role]} role in non-BSOL area`,
                { tags: 'regression' },
                () => {
                    cy.login(Roles.GP_ADMIN, false);

                    cy.url().should('eq', baseUrl + homeUrl);
                    cy.get('h1').should(
                        'include.text',
                        'You’re outside of Birmingham and Solihull (BSOL)',
                    );
                    cy.title().should(
                        'eq',
                        'Access to this service outside of Birmingham and Solihull - Digital Lloyd George records',
                    );
                    cy.get('.govuk-warning-text__text').should('exist');
                    cy.get('.govuk-warning-text__text').should(
                        'include.text',
                        'Downloading a record will remove it from our storage.',
                    );

                    cy.get('.nhsuk-header__navigation').should('exist');
                    cy.get('.nhsuk-header__navigation-list').should('exist');
                },
            );
        });

        gpRoles.forEach((role) => {
            it(
                `should display patient search page when user is ${Roles[role]} role in BSOL area`,
                { tags: 'regression' },
                () => {
                    cy.login(role, true);

                    cy.url().should('eq', baseUrl + patientSearchUrl);
                    cy.get('h1').should(
                        'not.include.text',
                        'You’re outside of Birmingham and Solihull (BSOL)',
                    );

                    cy.get('.nhsuk-header__navigation').should('exist');
                    cy.get('.nhsuk-header__navigation-list').should('exist');
                },
            );
        });

        it(
            'should display patient search page when user is PCSE Role',
            { tags: 'regression' },
            () => {
                cy.login(Roles.PCSE);

                cy.url().should('eq', baseUrl + patientSearchUrl);
                cy.get('h1').should(
                    'not.include.text',
                    'You’re outside of Birmingham and Solihull (BSOL)',
                );

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

                cy.get('.nhsuk-header__navigation').should('exist');
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
