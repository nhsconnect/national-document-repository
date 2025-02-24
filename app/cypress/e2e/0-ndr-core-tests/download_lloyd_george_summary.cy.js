import { Roles } from '../../support/roles';
import dbItem from '../../fixtures/dynamo-db-items/active-patient.json';

const workspace = Cypress.env('WORKSPACE');
dbItem.FileLocation = dbItem.FileLocation.replace('{env}', workspace);
const tableName = `${workspace}_LloydGeorgeReferenceMetadata`;

const featureFlags = {
    downloadOdsReportEnabled: true,
};

describe('GP Workflow: Download Lloyd George summary report', () => {
    context('Download Lloyd George summary report', () => {
        it(
            'Authenticated user can download the Lloyd George summary csv',
            { tags: 'regression', defaultCommandTimeout: 20000 },
            () => {
                cy.login(Roles.GP_ADMIN, featureFlags);
                cy.navigateToDownloadReportPage();

                cy.intercept('GET', '/OdsReport*', (req) => {
                    req.reply({
                        statusCode: 200,
                        body: {
                            url: Cypress.config('baseUrl') + '/browserconfig.xml',
                        },
                    });
                }).as('downloadReportFinished');

                cy.getByTestId('download-csv-button').click();

                cy.wait('@downloadReportFinished', { timeout: 20000 });

                cy.url().should(
                    'eq',
                    Cypress.config('baseUrl') + '/create-report/complete?reportType=0',
                );
            },
        );

        it(
            'Authenticated user can download the Lloyd George summary xlsx',
            { tags: 'regression', defaultCommandTimeout: 20000 },
            () => {
                cy.login(Roles.GP_ADMIN, featureFlags);
                cy.navigateToDownloadReportPage();

                cy.intercept('GET', '/OdsReport*', (req) => {
                    req.reply({
                        statusCode: 200,
                        body: {
                            url: Cypress.config('baseUrl') + '/browserconfig.xml',
                        },
                    });
                }).as('downloadReportFinished');

                cy.getByTestId('download-xlsx-button').click();

                cy.wait('@downloadReportFinished', { timeout: 20000 });

                cy.url().should(
                    'eq',
                    Cypress.config('baseUrl') + '/create-report/complete?reportType=0',
                );
            },
        );

        it(
            'Authenticated user can download the Lloyd George summary pdf',
            { tags: 'regression', defaultCommandTimeout: 20000 },
            () => {
                cy.login(Roles.GP_ADMIN, featureFlags);
                cy.navigateToDownloadReportPage();

                cy.intercept('GET', '/OdsReport*', (req) => {
                    req.reply({
                        statusCode: 200,
                        body: {
                            url: Cypress.config('baseUrl') + '/browserconfig.xml',
                        },
                    });
                }).as('downloadReportFinished');

                cy.getByTestId('download-pdf-button').click();

                cy.wait('@downloadReportFinished', { timeout: 20000 });

                cy.url().should(
                    'eq',
                    Cypress.config('baseUrl') + '/create-report/complete?reportType=0',
                );
            },
        );

        it(
            'Authenticated user cannot download summary when there are no patients held for their ods',
            { tags: 'regression', defaultCommandTimeout: 20000 },
            () => {
                cy.login(Roles.GP_ADMIN, featureFlags);
                cy.navigateToDownloadReportPage();

                cy.intercept('GET', '/OdsReport*', (req) => {
                    req.reply({
                        statusCode: 404,
                    });
                }).as('downloadReportEmpty');

                cy.getByTestId('download-csv-button').click();

                cy.wait('@downloadReportEmpty', { timeout: 20000 });

                cy.getByTestId('notification-banner-content')
                    .should('exist')
                    .should('include.text', 'Report could not be created');
            },
        );

        it(
            'Authenticated user is shown an error message when the download fails',
            { tags: 'regression', defaultCommandTimeout: 20000 },
            () => {
                cy.login(Roles.GP_ADMIN, featureFlags);
                cy.navigateToDownloadReportPage();

                cy.intercept('GET', '/OdsReport*', (req) => {
                    req.reply({
                        statusCode: 500,
                    });
                }).as('downloadReportFailed');

                cy.getByTestId('download-csv-button').click();

                cy.wait('@downloadReportFailed', { timeout: 20000 });

                cy.getByTestId('notification-banner-content')
                    .should('exist')
                    .should('include.text', 'Download failed');
            },
        );
    });
});
