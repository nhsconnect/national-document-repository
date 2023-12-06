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

const smokeTest = Cypress.env('CYPRESS_RUN_AS_SMOKETEST') ?? false;
const baseUrl = Cypress.config('baseUrl');

const forbiddenRoutes = [
    'search/patient/lloyd-george-record',
    'search/upload',
    'search/upload/result',
    'upload/submit',
];

describe('PCSE user role has access to the expected GP_ADMIN workflow paths', () => {
    context('PCSE role has access to expected routes', () => {
        it('PCSE role has access to Download View', () => {
            if (!smokeTest) {
                cy.intercept('GET', '/SearchPatient*', {
                    statusCode: 200,
                    body: patient,
                }).as('search');
            }

            cy.login('PCSE');

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
            it('PCSE role cannot access route' + forbiddenRoute, () => {
                cy.login('PCSE');
                cy.visit(baseUrl + forbiddenRoute);
                cy.url().should('include', 'unauthorised');
            });
        });
    });
});
