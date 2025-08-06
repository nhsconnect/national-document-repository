import { Roles, roleName } from '../../../support/roles';
import { routes } from '../../../support/routes';

describe('GP Workflow: Patient search and verify', () => {
    // env vars
    const baseUrl = Cypress.config('baseUrl');

    const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

    const noPatientError = 400;
    const testNotFoundPatient = '1000000001';
    const testPatient = '9000000009';
    let patient;

    gpRoles.forEach((role) => {
        beforeEach(() => {
            patient = {
                birthDate: '1970-01-01',
                familyName: 'Default Surname',
                givenName: ['Default Given Name'],
                nhsNumber: testPatient,
                postalCode: 'AA1 1AA',
                superseded: false,
                restricted: false,
                active: false,
            };
        });

        it(
            `Does not show verify patient view when the search finds no patient as ${roleName(
                role,
            )}`,
            { tags: 'regression' },
            () => {
                setup(role);
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
            `Shows the Lloyd george view page when upload patient is verified and active as a ${roleName(
                role,
            )} `,
            { tags: 'regression' },
            () => {
                setup(role);
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
                cy.url().should('eq', baseUrl + routes.lloydGeorgeView);
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
                setup(role);
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
                setup(role);
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

        it(
            'Does not show verify patient view when the user does not have access to the patient',
            { tags: 'regression' },
            () => {
                setup(role);
                cy.intercept('GET', '/SearchPatient*', (req) => {
                    req.reply({
                        statusCode: 404,
                        body: {
                            err_code: 'SP_4003',
                        },
                    });
                }).as('search');

                cy.get('#nhs-number-input').click();
                cy.get('#nhs-number-input').type(testNotFoundPatient);

                cy.get('#search-submit').click();
                cy.wait('@search');

                cy.get('#nhs-number-input--error-message').should('be.visible');
                cy.get('#nhs-number-input--error-message').should(
                    'include.text',
                    "Error: You cannot access this patient's record",
                );
                cy.get('#error-box-summary').should('be.visible');
                cy.get('#error-box-summary').should('have.text', 'There is a problem');
            },
        );
    });

    it.skip(
        `Shows patient upload screen when patient search is used as a
        GP_ADMIN and patient response is inactive`,
        { tags: 'regression' },
        () => {
            setup(Roles.GP_ADMIN);
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
            cy.title().should('eq', 'Patient details - Access and store digital patient documents');

            cy.url().should('include', 'verify');
            cy.url().should('eq', baseUrl + routes.patientVerify);
            cy.get('#gp-message').should('be.visible');
            cy.get('#gp-message').should(
                'have.text',
                'This page displays the current data recorded in the Personal Demographics Service for this patient.',
            );
            cy.get('#verify-submit').click();

            cy.url().should('include', 'upload');
            cy.url().should('eq', baseUrl + routes.arfUpload);
        },
    );

    it(
        'Does not show the upload documents page when upload patient is verified and inactive as a GP_Clinical',
        { tags: 'regression' },
        () => {
            setup(Roles.GP_CLINICAL);

            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(testPatient);

            cy.get('#search-submit').click();
            cy.wait('@search');

            cy.get('#nhs-number-input--error-message').should('be.visible');
            cy.get('#nhs-number-input--error-message').should(
                'include.text',
                "Error: You cannot access this patient's record",
            );
            cy.get('#error-box-summary').should('be.visible');
            cy.get('#error-box-summary').should('have.text', 'There is a problem');
        },
    );

    it(
        'Does not show the upload documents page when upload patient is disabled and patient is inactive as a GP_ADMIN',
        { tags: 'regression' },
        () => {
            setup(Roles.GP_ADMIN, {
                uploadArfWorkflowEnabled: false,
            });

            cy.intercept('GET', '/SearchPatient*', (req) => {
                req.reply({
                    statusCode: 200,
                    body: patient,
                });
            }).as('search');

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(testPatient);

            cy.get('#search-submit').click();
            cy.wait('@search');

            cy.get('#nhs-number-input--error-message').should('be.visible');
            cy.get('#nhs-number-input--error-message').should(
                'include.text',
                "Error: You cannot access this patient's record",
            );
            cy.get('#error-box-summary').should('be.visible');
            cy.get('#error-box-summary').should('have.text', 'There is a problem');
        },
    );
});

function setup(role, featureFlags) {
    cy.login(role, featureFlags);
    cy.visit(routes.patientSearch);
}
