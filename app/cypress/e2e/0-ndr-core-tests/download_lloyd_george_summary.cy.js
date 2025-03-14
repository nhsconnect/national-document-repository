import { Roles } from '../../support/roles';
import dbItem from '../../fixtures/dynamo-db-items/active-patient.json';
import { routes } from '../../support/routes';

const workspace = Cypress.env('WORKSPACE');
dbItem.FileLocation = dbItem.FileLocation.replace('{env}', workspace);

const featureFlags = {
    downloadOdsReportEnabled: true,
};

describe('GP Workflow: Download Lloyd George summary report', () => {
    context('Download Lloyd George summary report', () => {
        const fileTypes = ['csv', 'xlsx', 'pdf'];
        fileTypes.forEach((fileType) => {
            it(
                `Authenticated user can download the Lloyd George summary ${fileType}`,
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

                    cy.getByTestId(`download-${fileType}-button`).click();

                    cy.wait('@downloadReportFinished', { timeout: 20000 });

                    cy.url().should(
                        'eq',
                        Cypress.config('baseUrl') + `${routes.createReportComplete}?reportType=0`,
                    );
                },
            );
        });

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

        it(
            'Expired authenticated user is navigated to the session expiry screen when they attempt to download',
            { tags: 'regression', defaultCommandTimeout: 20000 },
            () => {
                cy.login(Roles.GP_ADMIN, featureFlags);
                cy.navigateToDownloadReportPage();

                cy.intercept('GET', '/OdsReport*', (req) => {
                    req.reply({
                        statusCode: 403,
                    });
                }).as('downloadReportFailed');

                cy.getByTestId('download-csv-button').click();

                cy.wait('@downloadReportFailed', { timeout: 20000 });

                cy.url().should('eq', Cypress.config('baseUrl') + routes.sessionExpired);
            },
        );
    });
});
