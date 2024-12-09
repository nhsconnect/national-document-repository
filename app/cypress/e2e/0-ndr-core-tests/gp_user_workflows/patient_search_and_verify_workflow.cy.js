import { Roles, roleName } from '../../../support/roles';

describe('GP Workflow: Patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.config('baseUrl');

    const patientSearchUrl = '/patient/search';
    const patientVerifyUrl = '/patient/verify';
    const lloydGeorgeViewUrl = '/patient/lloyd-george-record';
    const arfUploadUrl = '/patient/arf/upload';

    const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

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

    const featureFlags = {
        uploadArfWorkflowEnabled: 'true',
        uploadLambdaEnabled: 'true',
    };

    gpRoles.forEach((role) => {
        beforeEach(() => {
            cy.intercept('GET', '/FeatureFlags*', {
                statusCode: 200,
                body: featureFlags,
            }).as('featureFlags');

            cy.login(role);
            cy.visit(patientSearchUrl);
        });

        afterEach(() => {
            patient.active = false;
        });
        it(
            `Shows patient upload screen when patient search is used by as a
               ${roleName(role)} and patient response is inactive`,
            { tags: 'regression' },
            () => {
                cy.intercept('GET', '/SearchPatient*', {
                    statusCode: 200,
                    body: patient,
                }).as('search');

                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(testPatient);
                cy.title().should(
                    'eq',
                    'Search for a patient - Access and store digital patient documents',
                );

                cy.get('#search-submit').click();
                cy.wait('@search');
                cy.title().should(
                    'eq',
                    'Verify patient details - Access and store digital patient documents',
                );

                cy.url().should('include', 'verify');
                cy.url().should('eq', baseUrl + patientVerifyUrl);
                cy.get('#gp-message').should('be.visible');
                cy.get('#gp-message').should(
                    'have.text',
                    'Check these patient details match the records or attachments you plan to use',
                );
                cy.get('#verify-submit').click();

                cy.url().should('include', 'upload');
                cy.url().should('eq', baseUrl + arfUploadUrl);
            },
        );

        it(
            `Does not show verify patient view when the search finds no patient as ${roleName(
                role,
            )}`,
            { tags: 'regression' },
            () => {
                cy.intercept('GET', '/SearchPatient*', {
                    statusCode: noPatientError,
                }).as('search');

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
            `Shows the upload documents page when upload patient is verified and inactive as a ${roleName(
                role,
            )} `,
            { tags: 'regression' },
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

                cy.url().should('include', 'upload');
                cy.url().should('eq', baseUrl + arfUploadUrl);
            },
        );

        it(
            `Shows the Lloyd george view page when upload patient is verified and active as a ${roleName(
                role,
            )} `,
            { tags: 'regression' },
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
                cy.url().should('eq', baseUrl + lloydGeorgeViewUrl);
                cy.title().should(
                    'eq',
                    'Available records - Access and store digital patient documents',
                );
            },
        );

        it(
            `Search validation is shown when the user does not enter an nhs number as a ${roleName(
                role,
            )}`,
            { tags: 'regression' },
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
            `Search validation is shown when the user enters an invalid nhs number as a ${roleName(
                role,
            )} `,
            { tags: 'regression' },
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
