const { Roles } = require('../../../support/roles');

const testPatient = '9000000009';
const patient = {
    birthDate: '1970-01-01',
    familyName: 'Default Surname',
    givenName: ['Default Given Name'],
    nhsNumber: testPatient,
    postalCode: 'AA1 1AA',
    superseded: false,
    restricted: false,
    active: true,
};

const baseUrl = Cypress.config('baseUrl');

const forbiddenRoutes = ['/search/patient', '/search/patient/result', '/search/results'];

const clickSearchPatientButton = async () => {
    cy.getByTestId('search-patient-btn').click();
};

const bsolOptions = [true, false];

describe('GP Admin user role has access to the expected GP_ADMIN workflow paths', () => {
    bsolOptions.forEach((isBSOL) => {
        const prefix = isBSOL ? '[BSOL]' : '[Non-BSOL]';
        context(`${prefix} GP Admin role has access to expected routes`, () => {
            it('GP Admin role has access to Lloyd George View', { tags: 'regression' }, () => {
                cy.intercept('GET', '/SearchPatient*', {
                    statusCode: 200,
                    body: patient,
                }).as('search');

                cy.login(Roles.GP_ADMIN, isBSOL);
                if (!isBSOL) {
                    clickSearchPatientButton();
                }

                cy.url().should('eq', baseUrl + '/search/upload');

                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(testPatient);
                cy.get('#search-submit').click();
                cy.wait('@search');

                cy.url().should('include', 'upload');
                cy.url().should('eq', baseUrl + '/search/upload/result');

                cy.get('#verify-submit').click();

                cy.url().should('include', 'lloyd-george-record');
                cy.url().should('eq', baseUrl + '/search/patient/lloyd-george-record');
            });
        });
    });
});

describe('GP Admin user role cannot access expected forbidden routes', () => {
    bsolOptions.forEach((isBSOL) => {
        const prefix = isBSOL ? '[BSOL]' : '[Non-BSOL]';
        context(`${prefix} GP Admin role has no access to forbidden routes`, () => {
            forbiddenRoutes.forEach((forbiddenRoute) => {
                it(
                    'GP Admin role cannot access route ' + forbiddenRoute,
                    { tags: 'regression' },
                    () => {
                        cy.login(Roles.GP_ADMIN, isBSOL);
                        cy.visit(forbiddenRoute);
                        cy.url().should('include', 'unauthorised');
                    },
                );
            });
        });
    });
});

describe('GP Admin user of non-BSOL area are diverted to non-BSOL landing page upon login', () => {
    context('Non-BSOL GP Admin landing page', () => {
        it('Non-BSOL GP Admin user see a landing page upon login', { tags: 'regression' }, () => {
            cy.login(Roles.GP_ADMIN, false);

            cy.get('h1').should('include.text', 'You’re outside of Birmingham and Solihull (BSOL)');

            cy.getByTestId('search-patient-btn').click();

            cy.url().should('eq', baseUrl + '/search/upload');
        });
    });
});
