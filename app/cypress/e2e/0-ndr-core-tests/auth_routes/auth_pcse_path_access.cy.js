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
    active: false,
};

const baseUrl = Cypress.config('baseUrl');

const forbiddenRoutes = [
    '/search/patient/lloyd-george-record',
    '/search/upload',
    '/search/upload/result',
    '/upload/submit',
];

describe('PCSE user role has access to the expected GP_ADMIN workflow paths', () => {
    context('PCSE role has access to expected routes', () => {
        it('PCSE role has access to Download View', { tags: 'regression' }, () => {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');

            cy.login(Roles.PCSE);

            cy.getByTestId('search-patient-btn').should('exist');
            cy.getByTestId('search-patient-btn').click();
            cy.url().should('eq', baseUrl + '/search/patient');

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(testPatient);
            cy.get('#search-submit').click();
            cy.wait('@search');

            cy.get('#verify-submit').click();
            cy.url().should('eq', baseUrl + '/search/results');
        });
    });
});

describe('PCSE user role cannot access expected forbidden routes', () => {
    context('PCSE role has no access to forbidden routes', () => {
        forbiddenRoutes.forEach((forbiddenRoute) => {
            it('PCSE role cannot access route' + forbiddenRoute, { tags: 'regression' }, () => {
                cy.login(Roles.PCSE);
                cy.visit(forbiddenRoute);
                cy.url().should('include', 'unauthorised');
            });
        });
    });
});
