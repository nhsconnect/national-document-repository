describe('GP Upload Workflow Step 1: Patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';
    const smokeTest = Cypress.env('CYPRESS_RUN_AS_SMOKETEST') ?? false;

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
        active: false,
    };

    beforeEach(() => {
        cy.login('GP_ADMIN');
    });

    it('(Smoke test) shows patient upload screen when patient search is used by a GP and Inactive patient radio button is selected', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');
        }

        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);

        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.url().should('include', 'upload');
        cy.url().should('eq', baseUrl + 'search/upload/result');
        cy.get('#gp-message').should('be.visible');
        cy.get('#gp-message').should(
            'have.text',
            'Ensure these patient details match the records and attachments that you upload',
        );
        cy.get('#verify-submit').click();

        cy.url().should('include', 'submit');
        cy.url().should('eq', baseUrl + 'upload/submit');
    });

    it('(Smoke test) does not show verify patient when the search finds no patient', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: noPatientError,
            }).as('search');
        }

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

    it('shows the upload documents page when upload patient is verified and Inactive patient radio button selected', () => {
        cy.intercept('GET', '/SearchPatient*', {
            statusCode: 200,
            body: patient,
        }).as('search');
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);
        cy.get('#search-submit').click();
        cy.wait('@search');

        cy.get('#verify-submit').click();

        cy.url().should('include', 'submit');
        cy.url().should('eq', baseUrl + 'upload/submit');
    });

    it("fails to search for a patient when the user doesn't enter an nhs number", () => {
        cy.get('#search-submit').click();
        cy.get('#nhs-number-input--error-message').should('be.visible');
        cy.get('#nhs-number-input--error-message').should(
            'have.text',
            "Error: Enter patient's 10 digit NHS number",
        );
    });

    it('fails to search for a patient when the user enters an invalid nhs number', () => {
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
