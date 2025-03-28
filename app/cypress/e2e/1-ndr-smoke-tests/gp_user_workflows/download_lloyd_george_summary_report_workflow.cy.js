import { Roles } from '../../../support/roles';
import dbItem from '../../../fixtures/dynamo-db-items/active-patient.json';
import { routes } from '../../../support/routes';

const workspace = Cypress.env('WORKSPACE');
dbItem.FileLocation = dbItem.FileLocation.replace('{env}', workspace);
const tableName = `${workspace}_LloydGeorgeReferenceMetadata`;

describe('GP Workflow: Download Lloyd George summary report', () => {
    context('Download Lloyd George summary report', () => {
        beforeEach(() => {
            cy.deleteItemFromDynamoDb(tableName, dbItem.ID);
            cy.addItemToDynamoDb(tableName, dbItem);
        });

        afterEach(() => {
            cy.deleteItemFromDynamoDb(tableName, dbItem.ID);
        });

        it(
            '[Smoke] Authenticated user can download the Lloyd George summary',
            { tags: 'smoke', defaultCommandTimeout: 20000 },
            () => {
                cy.smokeLogin(Roles.GP_ADMIN);

                cy.navigateToDownloadReportPage();

                cy.intercept('GET', '/OdsReport*').as('downloadReportFinished');

                cy.getByTestId('download-csv-button').click();

                cy.wait('@downloadReportFinished', { timeout: 20000 });

                cy.url().should(
                    'eq',
                    Cypress.config('baseUrl') + `${routes.createReportComplete}?reportType=0`,
                );

                cy.getByTestId('logout-btn').click();
                cy.url({ timeout: 10000 }).should('eq', Cypress.config('baseUrl') + '/');
                cy.get('.nhsuk-header__navigation').should('not.exist');
            },
        );
    });
});
