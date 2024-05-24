const { Roles } = require('../../../support/roles');

describe('PCSE Workflow: patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.config('baseUrl');

    const patientSearchUrl = '/patient/search';
    const patientVerifyUrl = '/patient/verify';
    const lloydGeorgeViewUrl = '/patient/lloyd-george-record/';
    const arfDownloadUrl = '/patient/arf';
    const arfUploadUrl = '/patient/arf/upload';

    const homeUrl = '/';
    const patient = {
        birthDate: '1970-01-01',
        familyName: 'Default Surname',
        givenName: ['Default Given Name'],
        nhsNumber: '9000000009',
        postalCode: 'AA1 1AA',
        superseded: false,
        restricted: false,
    };

    beforeEach(() => {
        cy.visit(homeUrl);
        cy.login(Roles.PCSE);
    });

    it(
        'It shows the download documents page when download patient is verified by a PCSE user',
        { tags: 'regression' },
        () => {
            const testPatient = '9000000009';
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(testPatient);
            cy.get('#search-submit').click();
            cy.wait('@search');
            cy.get('#verify-submit').click();

            cy.url().should('eq', baseUrl + arfDownloadUrl);
        },
    );

    it(
        'It searches for a valid patient successfully when the user enters a known nhs number with spaces by a PCSE user',
        { tags: 'regression' },
        () => {
            const testPatient = '900 000 0009';
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: {
                    data: patient,
                },
            }).as('search');

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(testPatient);

            cy.get('#search-submit').click();
            cy.wait('@search');

            cy.url().should('include', 'verify');
            cy.url().should('eq', baseUrl + patientVerifyUrl);
        },
    );

    it(
        'It searches for a valid patient successfully when the user enters a known nhs number with dashes by a PCSE user',
        { tags: 'regression' },
        () => {
            const testPatient = '900-000-0009';
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: {
                    data: patient,
                },
            }).as('search');

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(testPatient);

            cy.get('#search-submit').click();
            cy.wait('@search');

            cy.url().should('include', 'verify');
            cy.url().should('eq', baseUrl + patientVerifyUrl);
        },
    );
});
