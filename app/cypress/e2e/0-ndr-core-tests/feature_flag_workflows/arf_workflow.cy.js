import { Roles, roleName } from '../../../support/roles';

const baseUrl = Cypress.config('baseUrl');
const searchPatientUrl = '/search/patient';

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

const navigateToUploadPage = () => {
    cy.intercept('GET', '/SearchPatient*', {
        statusCode: 200,
        body: patient,
    }).as('search');

    cy.visit(searchPatientUrl);
    cy.get('#nhs-number-input').click();
    cy.get('#nhs-number-input').type(testPatient);

    cy.get('#search-submit').click();
    cy.wait('@search');

    cy.get('#verify-submit').click();
};

const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

describe('Feature flags - ARF Workflow', () => {
    gpRoles.forEach((role) => {
        context(`As a ${roleName(role)} user visiting the ARF page for an inactive patient`, () => {
            it(
                'displays the page when both feature flags are enabled',
                { tags: 'regression' },
                () => {
                    cy.login(role);
                    navigateToUploadPage();

                    cy.url().should('include', 'upload');
                    cy.url().should('eq', baseUrl + '/patient/upload');
                    cy.get('h1').should('not.have.text', 'Unauthorised access');
                },
            );

            it(
                'displays the unauthorised page when ARF workflow feature flag is disabled',
                { tags: 'regression' },
                () => {
                    const featureFlags = {
                        uploadArfWorkflowEnabled: false,
                        uploadLambdaEnabled: true,
                    };
                    cy.login(role, true, featureFlags);
                    navigateToUploadPage();

                    cy.url().should('eq', baseUrl + '/unauthorised');
                    cy.get('h1').should('have.text', 'Unauthorised access');
                },
            );

            it(
                'displays the unauthorised page when upload lambda feature flag is disabled',
                { tags: 'regression' },
                () => {
                    const featureFlags = {
                        uploadArfWorkflowEnabled: true,
                        uploadLambdaEnabled: false,
                    };

                    cy.login(role, true, featureFlags);
                    navigateToUploadPage();

                    cy.url().should('eq', baseUrl + '/unauthorised');
                    cy.get('h1').should('have.text', 'Unauthorised access');
                },
            );

            it(
                'displays the unauthorised page when both upload and ARF workflow feature flag are disabled',
                { tags: 'regression' },
                () => {
                    const featureFlags = {
                        uploadArfWorkflowEnabled: false,
                        uploadLambdaEnabled: false,
                    };

                    cy.login(role, true, featureFlags);
                    navigateToUploadPage();

                    cy.url().should('eq', baseUrl + '/unauthorised');
                    cy.get('h1').should('have.text', 'Unauthorised access');
                },
            );
        });
    });
});
