describe('Patient search and verify', () => {
    const roles = Object.freeze({
        GP: 'gp',
        PCSE: 'pcse',
    });
    const baseUrl = 'http://localhost:3000/';
    const patientError = 400;
    const notFoundError = 404;
    const serviceError = 500;
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
        cy.get('#start-button').click();
        cy.get(`#${role}-radio-button`).click();
        cy.get('#role-submit-button').click();
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type('9000000009');
        cy.get('#search-submit').click();

        cy.wait(20);
    };

    it('(Smoke test) searches for a patient when the user enters an nhs number with spaces', () => {
        nagivateToSearch(roles.GP);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type('9000000009');
        cy.get('#search-submit').click();

        cy.url().should('include', 'result');
        cy.url().should('eq', baseUrl + 'search/patient/result');
    });

    it('(Smoke test) searches for a patient when the user enters an nhs number with spaces', () => {
        nagivateToSearch(roles.GP);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type('900 000 0009');
        cy.get('#search-submit').click();

        cy.url().should('include', 'result');
        cy.url().should('eq', baseUrl + 'search/patient/result');
    });
    it('(Smoke test) searches for a patient when the user enters an nhs number with dashed', () => {
        nagivateToSearch(roles.GP);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type('900-000-0009');
        cy.get('#search-submit').click();

        cy.url().should('include', 'result');
        cy.url().should('eq', baseUrl + 'search/patient/result');
    });

    it("(Smoke test) fails to search for a patient when the user doesn't enter an nhs number", () => {
        nagivateToSearch(roles.GP);
        cy.get('#search-submit').click();
        cy.get('#nhs-number-input--error-message').should('be.visible');
        cy.get('#nhs-number-input--error-message').should(
            'have.text',
            "Error: Enter patient's 10 digit NHS number",
        );
    });

    it('(Smoke test) fails to search for a patient when the user enters an invalid nhs number', () => {
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

    it.only('(Smoke test) fails to search for a patient when the lambda finds no patient', () => {
        const notFoundPatient = '1000000001';
        nagivateToSearch(roles.GP);
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(notFoundPatient);
        cy.get('#search-submit').click();
        cy.get('#nhs-number-input--error-message').should('be.visible');
        cy.get('#nhs-number-input--error-message').should(
            'have.text',
            'Error: Enter a valid patient NHS number.',
        );
        cy.get('#error-box-summary').should('be.visible');
        cy.get('#error-box-summary').should('have.text', 'There is a problem');
    });
});
