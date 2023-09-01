describe('Uploads docs and tests it looks OK', () => {
    const localhost = 'https://ndra.access-request-fulfilment.patient-deductions.nhs.uk/'

    beforeEach(() => {
        cy.visit(localhost)
    })

    const uploadedFilePathNames = [
        "cypress/fixtures/test_patient_record.pdf",
        "cypress/fixtures/test_patient_record_two.pdf",
    ]

    const uploadedImagesPathNames = [
        "cypress/fixtures/test-images/test_image.jpg",
        "cypress/fixtures/test-images/test_image_two.jpg",
        "cypress/fixtures/test-images/test_image_three.jpg",
        "cypress/fixtures/test-images/test_image_four.jpg",
        "cypress/fixtures/test-images/test_image_five.jpg",
        "cypress/fixtures/test-images/test_image_six.jpg",
        "cypress/fixtures/test-images/test_image_seven.jpg",
        "cypress/fixtures/test-images/test_image_eight.jpg",
        "cypress/fixtures/test-images/test_image_nine.jpg",
        "cypress/fixtures/test-images/test_image_ten.jpg",
        "cypress/fixtures/test-images/test_image_eleven.jpg",
    ]

    it('On Start now button click, redirect to uploads is successful', () => {

        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.url().should('include', 'upload')
        cy.url().should('eq', localhost + 'upload')

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

    // it('On Upload button click, renders Uploading Stage', () => {
    //
    //     cy.get('.nhsuk-button').click()
    //     cy.wait(20)
    //     cy.get("input[type=file]").selectFile(uploadedFilePathNames[0])
    //     cy.get("#upload-button").click()
    //     cy.get('#uploading-stage-warning').should('be.visible')
    //
    // })


    it('Single file - On Upload button click, renders Upload Summary for successful upload', () => {

        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.get("input[type=file]").selectFile(uploadedFilePathNames[0])
        cy.get("#upload-button").click()
        cy.wait(20)
        cy.get("#upload-summary-confirmation").should('be.visible')
        cy.get("#upload-summary-header").should('be.visible')
        cy.get('#successful-uploads').should('be.visible')
        cy.get("#successful-uploads").should('have.length', 1)
        cy.get("#successful-uploads tbody tr").first().get('td').first().should('contain', 'test_patient_record.pdf')
        cy.get('#close-page-warning').should('be.visible')
        cy.get('#start-again-button').should('have.text', 'Start Again')
        cy.get('#start-again-button').click()
        cy.url().should('eq', localhost)

    })

    it('Single file - On Upload button click, renders Upload Summary with error box when DocumentReference returns a 500', () => {
        // intercept this response and return an error
        cy.intercept('POST', '*/DocumentReference*', {
            statusCode: 500,
        })
        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.get("input[type=file]").selectFile(uploadedFilePathNames[0])
        cy.get("#upload-button").click()
        cy.wait(20)
        cy.get('#failed-document-uploads-summary-title').should('be.visible')
        cy.get('#failed-uploads').should('be.visible')
        cy.get("#failed-uploads tbody tr").should('have.length', 1)
        cy.get("#failed-uploads tbody tr").first().get('td').first().should('contain', 'test_patient_record.pdf')
        cy.get('#failed-uploads').should('contain', '1 of 1 files failed to upload')
        cy.get('#close-page-warning').should('be.visible')
        cy.get('#start-again-button').should('have.text', 'Start Again')
        cy.get('#start-again-button').click()
        cy.url().should('eq', localhost)

    })

    it('Single file - On Upload button click, renders Upload Summary with error box when DocumentReference returns a 404', () => {
        // intercept this response and return an error
        cy.intercept('POST', '*/DocumentReference*', {
            statusCode: 404,
        })
        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.get("input[type=file]").selectFile(uploadedFilePathNames[0])
        cy.get("#upload-button").click()
        cy.wait(20)
        cy.get('#failed-document-uploads-summary-title').should('be.visible')
        cy.get('#failed-uploads').should('be.visible')
        cy.get("#failed-uploads tbody tr").should('have.length', 1)
        cy.get("#failed-uploads tbody tr").first().get('td').first().should('contain', 'test_patient_record.pdf')
        cy.get('#failed-uploads').should('contain', '1 of 1 files failed to upload')
        cy.get('#close-page-warning').should('be.visible')
        cy.get('#start-again-button').should('have.text', 'Start Again')
        cy.get('#start-again-button').click()
        cy.url().should('eq', localhost)

    })

    // once authorisation functionality has been added we can include a test like below for s3 bucket POST failure with 403 status
    it('Single file - On Upload button click, renders Upload Summary with error box when the s3 bucket POST request fails', () => {
        // intercept this response and return an error
        cy.intercept('POST', 'https://ndra-document-store.s3.amazonaws.com/', {
            statusCode: 500,
        })
        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.get("input[type=file]").selectFile(uploadedFilePathNames[0])
        cy.get("#upload-button").click()
        cy.wait(20)
        cy.get('#failed-document-uploads-summary-title').should('be.visible')
        cy.get('#failed-uploads').should('be.visible')
        cy.get("#failed-uploads tbody tr").should('have.length', 1)
        cy.get("#failed-uploads tbody tr").first().get('td').first().should('contain', 'test_patient_record.pdf')
        cy.get('#failed-uploads').should('contain', '1 of 1 files failed to upload')
        cy.get('#close-page-warning').should('be.visible')
        cy.get('#start-again-button').should('have.text', 'Start Again')
        cy.get('#start-again-button').click()
        cy.url().should('eq', localhost)

    })

    it('Multiple files - On Choose files button click, file selection is visible', () => {

        cy.get('.nhsuk-button').click()
        cy.wait(20)
        cy.get("#selected-documents-table").should('not.exist')
        cy.get("input[type=file]").selectFile(uploadedFilePathNames)
        cy.get("#selected-documents-table").should('be.visible')
        cy.get("#selected-documents-table tbody tr").should('have.length', 2)
        cy.get("#selected-documents-table tbody tr").first().get('td').first().should('have.text', 'test_patient_record.pdf')
        cy.get("#selected-documents-table tbody tr").next().contains('td', 'test_patient_record_two.pdf')

    })
})