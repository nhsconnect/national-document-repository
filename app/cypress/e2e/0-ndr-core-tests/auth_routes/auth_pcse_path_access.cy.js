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
const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';
const forbiddenRoutes = [
    '/search/patient/lloyd-george-record',
    '/search/upload',
    '/search/upload/result',
    '/upload/submit',
];
const authUnauthorisedRoute = '/unauthorised';

describe('assert PCSE user has access to the PCSE workflow path ', () => {
    context('session management', () => {
        it('sets session storage on login and checks starting url route', () => {
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
            cy.url().should('eq', baseUrl + 'search/results');
        });
    });
});
