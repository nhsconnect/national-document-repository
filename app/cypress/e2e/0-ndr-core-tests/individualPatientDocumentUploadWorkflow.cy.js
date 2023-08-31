describe('Uploads docs and tests it looks OK', () => {
    beforeEach(() => {
        cy.visit('http://localhost:3000')
    })

    const uploadedFilePathNames = [
        "cypress/fixtures/test_patient_record.pdf",
        "cypress/fixtures/test_patient_record_two.pdf",
    ]

    it('On Start now button click, redirect to uploads is successful', () => {

        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.url().should('include', 'upload')
        cy.url().should('eq', 'http://localhost:3000/upload')

    })

    // Patient selection not implemented yet

    it('Single file - On Choose files button click, file selection is visible', () => {

        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.get("#selected-documents-table").should('not.exist')
        cy.get("input[type=file]").selectFile(uploadedFilePathNames[0])
        cy.get("#selected-documents-table").should('be.visible')
        cy.get("#selected-documents-table tbody tr").should('have.length', 1)
        cy.get("#selected-documents-table tbody tr").first().get('td').first().should('have.text', 'test_patient_record.pdf')

    })

    it('Single file - On Upload button click, renders Upload Summary with errors when upload has failed', () => {

        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.get("input[type=file]").selectFile(uploadedFilePathNames[0])
        cy.get("#upload-button").click()
        cy.get('#failed-document-uploads-summary-title').should('be.visible')
        cy.get('#failed-uploads').should('be.visible')
        cy.get("#failed-uploads tbody tr").should('have.length', 1)
        cy.get("#failed-uploads tbody tr").first().get('td').first().should('contain', 'test_patient_record.pdf')
        cy.get('#failed-uploads').should('contain', '1 of 1 files failed to upload')
        cy.get('#failed-upload-warning').should('be.visible')
        cy.get('#start-again-button').should('have.text', 'Start Again')
        cy.get('#start-again-button').click()
        cy.url().should('eq', 'http://localhost:3000/')

    })
})