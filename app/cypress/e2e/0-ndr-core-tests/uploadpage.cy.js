describe('Uploads docs and tests it looks OK', () => {
    beforeEach(() => {
    // Cypress starts out with a blank slate for each test
    // so we must tell it to visit our website with the `cy.visit()` command.
    // Since we want to visit the same URL at the start of all our tests,
    // we include it in our beforeEach function so that it runs before each test
    cy.visit('http://localhost:3000')
    })

    it('displays expected page header on home page', () => {
        const baseUrl = "http://localhost:3000";
        const uploadedFilePathNames = [
            "cypress/fixtures/test_patient_record.pdf",
            "cypress/fixtures/test_patient_record_two.pdf",
        ];
        cy.get('.nhsuk-button').click()

        cy.url().should("eq", baseUrl + "/upload");

        cy.get("input[type=file]").selectFile(uploadedFilePathNames);
        cy.get('.nhsuk-button').click()
  })
})