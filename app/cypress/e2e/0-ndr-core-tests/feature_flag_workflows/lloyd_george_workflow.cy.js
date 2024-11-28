import { Roles } from '../../../support/roles';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatient.json';

const beforeEachConfiguration = (role, featureFlags) => {
    cy.login(role, true, featureFlags);
    cy.intercept('GET', '/SearchPatient*', {
        statusCode: 200,
        body: searchPatientPayload,
    }).as('search');
    cy.getByTestId('nhs-number-input').type(searchPatientPayload.nhsNumber);
    cy.getByTestId('search-submit-btn').click();
    cy.wait('@search');
};

describe('Feature flags - Lloyd George Workflow', () => {
    context('As a GP admin BSOL user visiting Lloyd George record page', () => {
        it(
            'displays upload text and button when both upload feature flags are enabled',
            { tags: 'regression' },
            () => {
                const featureFlags = {
                    uploadLloydGeorgeWorkflowEnabled: true,
                    uploadLambdaEnabled: true,
                };
                beforeEachConfiguration(Roles.GP_ADMIN, featureFlags);
                cy.intercept('POST', '/LloydGeorgeStitch*', {
                    statusCode: 404,
                });
                cy.title().should(
                    'eq',
                    'Verify patient details - Access and store digital patient documents',
                );

                cy.get('#verify-submit').click();

                cy.getByTestId('upload-patient-record-text').should('exist');
                cy.getByTestId('upload-patient-record-button').should('exist');
                cy.title().should(
                    'eq',
                    'Available records - Access and store digital patient documents',
                );
                cy.contains('To search within the record use Control and F').should('exist');
            },
        );

        it(
            'does not display upload text and button when neither upload feature flags are enabled',
            { tags: 'regression' },
            () => {
                const featureFlags = {
                    uploadLloydGeorgeWorkflowEnabled: false,
                    uploadLambdaEnabled: false,
                };
                beforeEachConfiguration(Roles.GP_ADMIN, featureFlags);
                cy.intercept('POST', '/LloydGeorgeStitch*', {
                    statusCode: 404,
                });
                cy.get('#verify-submit').click();

                cy.getByTestId('upload-patient-record-text').should('not.exist');
                cy.getByTestId('upload-patient-record-button').should('not.exist');
            },
        );

        it(
            'does not display upload text and button when upload lambda feature flag is not enabled',
            { tags: 'regression' },
            () => {
                const featureFlags = {
                    uploadLloydGeorgeWorkflowEnabled: true,
                    uploadLambdaEnabled: false,
                };
                beforeEachConfiguration(Roles.GP_ADMIN, featureFlags);
                cy.intercept('POST', '/LloydGeorgeStitch*', {
                    statusCode: 404,
                });
                cy.get('#verify-submit').click();

                cy.getByTestId('upload-patient-record-text').should('not.exist');
                cy.getByTestId('upload-patient-record-button').should('not.exist');
            },
        );

        it(
            'does not display upload text and button when upload Lloyd George feature flag is not enabled',
            { tags: 'regression' },
            () => {
                const featureFlags = {
                    uploadLloydGeorgeWorkflowEnabled: false,
                    uploadLambdaEnabled: true,
                };
                beforeEachConfiguration(Roles.GP_ADMIN, featureFlags);
                cy.intercept('POST', '/LloydGeorgeStitch*', {
                    statusCode: 404,
                });
                cy.get('#verify-submit').click();

                cy.getByTestId('upload-patient-record-text').should('not.exist');
                cy.getByTestId('upload-patient-record-button').should('not.exist');
            },
        );
    });
});
