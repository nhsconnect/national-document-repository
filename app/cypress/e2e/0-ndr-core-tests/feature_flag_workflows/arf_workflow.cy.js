import { Roles, roleName } from '../../../support/roles';
import { routes } from '../../../support/routes';

const baseUrl = Cypress.config('baseUrl');

const arfUploadUrl = '/patient/arf/upload';
const unauthorisedUrl = '/unauthorised';

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
    deceased: false,
};

const navigateToUploadPage = () => {
    cy.intercept('GET', '/SearchPatient*', {
        statusCode: 200,
        body: patient,
    }).as('search');

    cy.visit(routes.patientSearch);
    cy.get('#nhs-number-input').click();
    cy.get('#nhs-number-input').type(testPatient);

    cy.get('#search-submit').click();
    cy.wait('@search');
};

const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

describe('Feature flags - ARF Workflow', () => {
    it(
        'for GP clinical role it does not find patient when both feature flags are enabled',
        { tags: 'regression' },
        () => {
            cy.login(Roles.GP_CLINICAL);
            navigateToUploadPage();
            cy.get('#nhs-number-input--error-message').should('be.visible');
            cy.get('#nhs-number-input--error-message').should(
                'include.text',
                "Error: You cannot access this patient's record",
            );
            cy.get('#error-box-summary').should('be.visible');
            cy.get('#error-box-summary').should('have.text', 'There is a problem');
        },
    );
    gpRoles.forEach((role) => {
        context(`As a ${roleName(role)} user visiting the ARF page for an inactive patient`, () => {
            it(
                'displays the error when ARF workflow feature flag is disabled',
                { tags: 'regression' },
                () => {
                    const featureFlags = {
                        uploadArfWorkflowEnabled: false,
                        uploadLambdaEnabled: true,
                    };
                    cy.login(role, featureFlags);
                    navigateToUploadPage();

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
                'displays the error page when upload lambda feature flag is disabled',
                { tags: 'regression' },
                () => {
                    const featureFlags = {
                        uploadArfWorkflowEnabled: true,
                        uploadLambdaEnabled: false,
                    };

                    cy.login(role, featureFlags);
                    navigateToUploadPage();

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
                'displays the error page when both upload and ARF workflow feature flag are disabled',
                { tags: 'regression' },
                () => {
                    const featureFlags = {
                        uploadArfWorkflowEnabled: false,
                        uploadLambdaEnabled: false,
                    };

                    cy.login(role, featureFlags);
                    navigateToUploadPage();

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
    });
});
