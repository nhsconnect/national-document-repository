describe('GP Workflow: Patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.config('baseUrl');
    const smokeTest = Cypress.env('CYPRESS_RUN_AS_SMOKETEST') ?? false;
    const gpRoles = ['GP_ADMIN', 'GP_CLINICAL'];

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

    gpRoles.forEach((role) => {
        beforeEach(() => {
            cy.login(role);
        });

        afterEach(() => {
            patient.active = false;
        });

        it(
            '(Smoke test) Shows patient upload screen when patient search is used by a ' +
                role +
                ' role and patient response is inactive',
            () => {
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
                cy.url().should('eq', baseUrl + '/search/upload/result');
                cy.get('#gp-message').should('be.visible');
                cy.get('#gp-message').should(
                    'have.text',
                    'Ensure these patient details match the records and attachments that you upload',
                );
                cy.get('#verify-submit').click();

                cy.url().should('include', 'submit');
                cy.url().should('eq', baseUrl + '/upload/submit');
            },
        );

        it(
            '(Smoke test) Does not show verify patient view when the search finds no patient as a ' +
                role +
                ' role',
            () => {
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
            },
        );

        it(
            'Shows the upload documents page when upload patient is verified and inactive as a ' +
                role +
                ' role',
            () => {
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
                cy.url().should('eq', baseUrl + '/upload/submit');
            },
        );

        it(
            'Shows the Lloyd george view page when upload patient is verified and active as a ' +
                role +
                ' role',
            () => {
                patient.active = true;

                cy.intercept('GET', '/SearchPatient*', {
                    statusCode: 200,
                    body: patient,
                }).as('search');

                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(testPatient);
                cy.get('#search-submit').click();
                cy.wait('@search');

                cy.get('#verify-submit').click();

                cy.url().should('include', 'lloyd-george-record');
                cy.url().should('eq', baseUrl + '/search/patient/lloyd-george-record');
            },
        );

        it(
            'Search validation is shown when the user does not enter an nhs number as a ' +
                role +
                ' role',
            () => {
                cy.get('#search-submit').click();
                cy.get('#nhs-number-input--error-message').should('be.visible');
                cy.get('#nhs-number-input--error-message').should(
                    'have.text',
                    "Error: Enter patient's 10 digit NHS number",
                );
            },
        );

        it(
            'Search validation is shown when the user enters an invalid nhs number as a ' +
                role +
                ' role',
            () => {
                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type('900');
                cy.get('#search-submit').click();
                cy.get('#nhs-number-input--error-message').should('be.visible');
                cy.get('#nhs-number-input--error-message').should(
                    'have.text',
                    "Error: Enter patient's 10 digit NHS number",
                );
            },
        );
    });
});
