describe('Patient search and verify', () => {
    const roles = Object.freeze({
        GP: 'gp',
        PCSE: 'pcse',
    });
    const environments = Object.freeze({
        local: 'local',
        dev: 'development',
    });

    const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';
    const smokeTest = Cypress.env('CYPRESS_RUN_AS_SMOKETEST') ?? false;
    const runEnvironment = Cypress.env('CYPRESS_RUN_ENVIRONMENT') ?? environments.dev;
    const isLocal = runEnvironment === environments.local;
    const testPatient = '9000000009';
    const testNotFoundPatient = '1000000001';

    const noPatientError = 400;

    const patient = {
        birthDate: '1970-01-01',
        familyName: 'Default Surname',
        givenName: ['Default Given Name'],
        nhsNumber: '0000000000',
        postalCode: 'AA1 1AA',
        superseded: false,
        restricted: false,
    };
    beforeEach(() => {
        cy.visit(baseUrl);
    });

    const nagivateToSearch = (role) => {
        cy.get('#start-button').click();
        cy.get(`#${role}-radio-button`).click();
        cy.get('#role-submit-button').click();

        cy.wait(20);
    };

    const navigateToVerify = (role) => {
        cy.intercept('GET', '/SearchPatient*', {
            statusCode: 200,
            body: patient,
        }).as('search');
        cy.get('#start-button').click();
        cy.get(`#${role}-radio-button`).click();
        cy.get('#role-submit-button').click();
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');
    };

    it('(Smoke test) shows patient upload screen when patient search is used by a GP', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');
        }

        nagivateToSearch(roles.GP);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.url().should('include', 'upload');
        cy.url().should('eq', baseUrl + 'search/upload/result');
        cy.get('#gp-message').should('be.visible');
        cy.get('#gp-message').should(
            'have.text',
            'Ensure these patient details match the electronic health records and attachments you are about to upload.',
        );
        cy.get('#verify-submit').click();

        cy.url().should('include', 'submit');
        cy.url().should('eq', baseUrl + 'upload/submit');
    });

    it('(Smoke test) shows patient download screen when patient search is used by PCSE', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');
        }
        nagivateToSearch(roles.PCSE);
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

    it('(Smoke test) does not show verify patient when the search finds no patient', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: noPatientError,
            }).as('search');
        }

        nagivateToSearch(roles.GP);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testNotFoundPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.get('#nhs-number-input--error-message').should('be.visible');
        cy.get('#nhs-number-input--error-message').should(
            'have.text',
            'Error: Enter a valid patient NHS number.',
        );
        cy.get('#error-box-summary').should('be.visible');
        cy.get('#error-box-summary').should('have.text', 'There is a problem');
    });

    it('shows the upload documents page when upload patient is verified', () => {
        navigateToVerify(roles.GP);
        cy.get('#verify-submit').click();

        cy.url().should('include', 'submit');
        cy.url().should('eq', baseUrl + 'upload/submit');
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

        nagivateToSearch(roles.PCSE);
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

        nagivateToSearch(roles.PCSE);
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

        nagivateToSearch(roles.PCSE);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.url().should('include', 'result');
        cy.url().should('eq', baseUrl + 'search/patient/result');
    });

    it("fails to search for a patient when the user doesn't enter an nhs number", () => {
        nagivateToSearch(roles.GP);
        cy.get('#search-submit').click();
        cy.get('#nhs-number-input--error-message').should('be.visible');
        cy.get('#nhs-number-input--error-message').should(
            'have.text',
            "Error: Enter patient's 10 digit NHS number",
        );
    });

    it('fails to search for a patient when the user enters an invalid nhs number', () => {
        nagivateToSearch(roles.GP);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type('900');
        cy.get('#search-submit').click();
        cy.get('#nhs-number-input--error-message').should('be.visible');
        cy.get('#nhs-number-input--error-message').should(
            'have.text',
            "Error: Enter patient's 10 digit NHS number",
        );
    });
});
