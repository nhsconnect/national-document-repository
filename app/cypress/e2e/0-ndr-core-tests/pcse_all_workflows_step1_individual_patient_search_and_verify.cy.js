describe('PCSE User all Workflows Step 1: Patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';
    const smokeTest = Cypress.env('CYPRESS_RUN_AS_SMOKETEST') ?? false;

    const roles = Object.freeze({
        GP: 'gp',
        PCSE: 'pcse',
    });

    const noPatientError = 400;
    const testNotFoundPatient = '1000000001';
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
    beforeEach(() => {
        cy.visit(baseUrl);
    });

    const navigateToSearch = (role) => {
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
        cy.wait('@auth');
        cy.get(`#${role}-radio-button`).click();
        cy.get('#role-submit-button').click();
    };

    const navigateToVerify = (role) => {
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
        cy.get(`#${role}-radio-button`).click();
        cy.get('#role-submit-button').click();
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);
        cy.get('#search-submit').click();
        cy.wait('@search');
    };

    it('(Smoke test) shows patient download screen when patient search is used by PCSE', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');
        }
        navigateToSearch(roles.PCSE);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.url().should('include', 'result');
        cy.url().should('eq', baseUrl + 'search/patient/result');
        cy.get('#gp-message').should('not.exist');

        cy.get('#verify-submit').click();

        cy.url().should('include', 'results');
        cy.url().should('eq', baseUrl + 'search/results');
    });

    it('shows the download documents page when download patient is verified', () => {
        navigateToVerify(roles.PCSE);
        cy.get('#verify-submit').click();

        cy.url().should('include', 'results');
        cy.url().should('eq', baseUrl + 'search/results');
    });

    it('(Smoke test) searches for a patient when the user enters an nhs number', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');
        }

        navigateToSearch(roles.PCSE);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.url().should('include', 'result');
        cy.url().should('eq', baseUrl + 'search/patient/result');
    });

    it('(Smoke test) searches for a patient when the user enters an nhs number with spaces', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: {
                    data: patient,
                },
            }).as('search');
        }

        navigateToSearch(roles.PCSE);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.url().should('include', 'result');
        cy.url().should('eq', baseUrl + 'search/patient/result');
    });

    it('(Smoke test) searches for a patient when the user enters an nhs number with dashed', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: {
                    data: patient,
                },
            }).as('search');
        }

        navigateToSearch(roles.PCSE);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.url().should('include', 'result');
        cy.url().should('eq', baseUrl + 'search/patient/result');
    });
});
