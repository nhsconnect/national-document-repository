// env vars
const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';
const smokeTest = Cypress.env('CYPRESS_RUN_AS_SMOKETEST') ?? false;

const roles = Object.freeze({
    GP: 'gp',
});

const testPatient = '9000000009';
const patient = {
    birthDate: '1970-01-01',
    familyName: 'Default Surname',
    givenName: ['Default Given Name'],
    nhsNumber: testPatient,
    postalCode: 'AA1 1AA',
    superseded: false,
    restricted: false,
};

const navigateToLgPage = () => {
    cy.visit(baseUrl + 'auth-callback');
    cy.intercept('GET', '/Auth/TokenRequest*', {
        statusCode: 200,
        body: {
            organisations: [
                {
                    org_name: 'PORTWAY LIFESTYLE CENTRE',
                    ods_code: 'A470',
                    role: 'DEV',
                },
            ],
            authorisation_token: '111xxx222',
        },
    }).as('auth');
    cy.intercept('GET', '/SearchPatient*', {
        statusCode: 200,
        body: patient,
    }).as('search');
    cy.wait('@auth');
    cy.get(`#${roles.GP}-radio-button`).click();
    cy.get('#role-submit-button').click();
    cy.get('#nhs-number-input').click();
    cy.get('#nhs-number-input').type(testPatient);

    cy.get('#search-submit').click();
    cy.wait('@search');

    cy.get('#active-radio-button').click();
    cy.get('#verify-submit').click();
};

beforeEach(() => {
    cy.visit(baseUrl);
    navigateToLgPage();
});

it('Navigates to Lloyd George record page successfully', () => {
    cy.url().should('eq', baseUrl + 'search/patient/lloyd-george-record');
});
