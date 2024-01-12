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

describe('GP Clinical user role has access to the expected GP_CLINICAL workflow paths', () => {
    context('GP Clinical role has access to expected routes', () => {
        it('GP Clinical role has access to Lloyd George View', { tags: 'regression' }, () => {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');

            cy.login(Roles.GP_CLINICAL);

            cy.getByTestId('search-patient-btn').should('exist');
            cy.getByTestId('search-patient-btn').click();
            cy.url().should('eq', baseUrl + '/search/upload');

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(testPatient);
            cy.get('#search-submit').click();
            cy.wait('@search');

            cy.url().should('include', 'result');
            cy.url().should('eq', baseUrl + '/search/result');

            cy.get('#verify-submit').click();

            cy.url().should('include', 'lloyd-george-record');
            cy.url().should('eq', baseUrl + '/search/patient/lloyd-george-record');
        });
    });
});

describe('GP Clinical user role cannot access expected forbidden routes', () => {
    context('GP Clinical role has no access to forbidden routes', () => {
        forbiddenRoutes.forEach((forbiddenRoute) => {
            it(
                'GP Clinical role cannot access route ' + forbiddenRoute,
                { tags: 'regression' },
                () => {
                    cy.login(Roles.GP_CLINICAL);
                    cy.visit(forbiddenRoute);
                    cy.url().should('include', 'unauthorised');
                },
            );
        });
    });
});
