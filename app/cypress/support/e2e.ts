import { DynamoDB, S3 } from 'aws-sdk';
import { Roles, roleIds, roleList } from './roles';
import { routes } from './routes';
import { defaultFeatureFlags, FeatureFlags } from './feature_flags';
import Bluebird from 'cypress/types/bluebird';
import './aws.commands';
import 'cypress-real-events';

/// <reference types="cypress" />
const registerCypressGrep = require('@cypress/grep');
registerCypressGrep();

Cypress.Commands.add('getByTestId', (selector, ...args) => {
    return cy.get(`[data-testid=${selector}]`, ...args);
});

Cypress.Commands.add('login', (role, featureFlags) => {
    if (roleIds.includes(role)) {
        const roleName = roleList.find((roleName) => Roles[roleName] === role);
        // Login for regression tests
        const authCallback = '/auth-callback';
        const fixturePath = 'requests/auth/GET_TokenRequest_' + roleName + '.json';

        cy.intercept('GET', '/Auth/TokenRequest*', {
            statusCode: 200,
            fixture: fixturePath,
        }).as('auth');

        if (featureFlags) {
            cy.intercept('GET', '/FeatureFlags*', {
                statusCode: 200,
                body: featureFlags,
            }).as('featureFlags');
        } else {
            cy.intercept('GET', '/FeatureFlags*', {
                statusCode: 200,
                body: defaultFeatureFlags,
            }).as('featureFlags');
        }

        cy.visit(authCallback);
        cy.wait('@auth');
        cy.wait('@featureFlags');
    } else {
        throw new Error("Invalid role for login. Only 'gp' or 'pcse' are allowed.");
    }
});

Cypress.Commands.add('smokeLogin', (role) => {
    // Login for smoke tests
    if (roleIds.includes(role)) {
        const baseUrl = Cypress.config('baseUrl');
        const username = Cypress.env('USERNAME');
        const password = Cypress.env('PASSWORD');

        const startUrl = '/';
        const authCallback = '/auth-callback';
        cy.visit(startUrl);
        cy.url().should('eq', baseUrl + startUrl);
        cy.get('.nhsuk-header__transactional-service-name--link').should(
            'have.text',
            'Access and store digital patient documents',
        );
        cy.get('.nhsuk-header__navigation').should('not.exist');
        cy.getByTestId('start-btn').should('exist');
        cy.getByTestId('start-btn').click();
        cy.origin(
            'https://am.nhsdev.auth-ptl.cis2.spineservices.nhs.uk',
            { args: { username, password, role } },
            (args) => {
                Cypress.on('uncaught:exception', () => false);
                const { username, password, role } = args;
                cy.url().should('include', 'cis2.spineservices.nhs.uk');
                cy.get('.nhsuk-cis2-cia-header-text').should('exist');
                cy.get('.nhsuk-cis2-cia-header-text').should('include.text', 'Authentication');
                cy.get('#floatingLabelInput19').should('exist');
                cy.get('#floatingLabelInput19').type(username);
                cy.get('#floatingLabelInput25').should('exist');
                cy.get('#floatingLabelInput25').type(password);

                cy.get('.nhsuk-button').should('exist');
                cy.get('.nhsuk-button').invoke('attr', 'type').should('eq', 'submit');
                cy.get('.nhsuk-button').click();
                cy.get(`#nhsRoleId_${role}`).should('exist');
                cy.get(`#nhsRoleId_${role}`).click();
            },
        );
        // cy.url().should('contain', baseUrl + authCallback);
        // cy.url({ timeout: 15000 }).should('not.contain', baseUrl + authCallback);
    } else {
        throw new Error("Invalid role for login. Only 'gp' or 'pcse' are allowed.");
    }
});

Cypress.Commands.add('navigateToHomePage', () => {
    const baseUrl = Cypress.config('baseUrl');

    cy.getByTestId('home-btn').click();
    cy.url().should('eq', baseUrl + routes.home);
});

Cypress.Commands.add('navigateToPatientSearchPage', () => {
    const baseUrl = Cypress.config('baseUrl');

    cy.navigateToHomePage();
    cy.getByTestId('search-patient-btn').should('exist');
    cy.getByTestId('search-patient-btn').click();

    cy.url().should('eq', baseUrl + routes.patientSearch);
});

Cypress.Commands.add('navigateToDownloadReportPage', () => {
    const baseUrl = Cypress.config('baseUrl');

    cy.navigateToHomePage();
    cy.getByTestId('download-report-btn').should('exist');
    cy.getByTestId('download-report-btn').click();

    cy.url().should('eq', baseUrl + `${routes.createReport}?reportType=0`);
});

declare global {
    namespace Cypress {
        interface Chainable {
            /**
             * Get DOM element by data-testid attribute.
             *
             * @param {string} value - The value of the data-testid attribute of the target DOM element.
             * @return {HTMLElement} - Target DOM element.
             */
            getByTestId(value: string): Chainable<JQuery<HTMLElement>>;
            /**
             * Mock user login by intercepting the {baseUrl}/auth-callback request
             * @param {Roles} role - The user role to login with. Must be an enum of Roles
             * @param featureFlags - Feature flags values to override the defaults
             */
            login(role: Roles, featureFlags?: FeatureFlags): Chainable<void>;

            /**
             * Real user login via CIS2 and redirect back to {baseUrl}/auth-callback.
             * @param {Roles} role - The user role to login with. Must be an enum of Roles
             */
            smokeLogin(role: Roles): Chainable<void>;
            /**
             * Add file to s3 bucket
             * @param {string} bucketName - Name of the target S3 bucket
             * @param {string} fileName - Filepath of the file to upload
             * @param {string} fileContent - Content of the file to upload
             * @return {Promise<SendData>} - S3 response for s3.upload
             */
            addPdfFileToS3(
                bucketName: string,
                fileName: string,
                filePath: string,
            ): Chainable<Bluebird<S3.ManagedUpload.SendData>>;
            /**
             * Add dynamoDB entry
             * @param {string} tableName - Name of the target dynamoDB table
             * @param {{ [key: string]: any; }} item - dynamoDB item to upload
             * @return {Promise<PutItemOutput>} - Dynamo response for dynamoDB.putItem
             */
            addItemToDynamoDb(
                tableName: string,
                item: DynamoDB.PutItemInputAttributeMap,
            ): Chainable<Bluebird<DynamoDB.PutItemOutput>>;
            /**
             * Delete file from S3 bucket
             * @param {string} bucketName - Name of the target S3 bucket
             * @param {string} fileName - Filepath of the file to delete
             * @return {Promise<DeleteObjectOutput>} - S3 response for s3.deleteObject
             */
            deleteFileFromS3(
                bucketName: string,
                fileName: string,
            ): Chainable<Bluebird<S3.DeleteObjectOutput>>;
            /**
             * Delete item from DynamoDB table
             * @param {string} tableName - Name of the target DynamoDB table
             * @param {string} itemId - ID of the item to delete
             * @return {Promise<DeleteItemOutput>} - Dynamo response for dynamoDB.deleteItem
             */
            deleteItemFromDynamoDb(
                tableName: string,
                itemId: string,
            ): Chainable<Bluebird<DynamoDB.DeleteItemOutput>>;
            /**
             * Delete items with a specific secondary key value from DynamoDB table
             * @param {string} tableName - Name of the target DynamoDB table
             * @param {string} index - Index for the secondary key
             * @param {string} attribute - Name of the attribute you are matching on
             * @param {string} value - Specific value you are matching on to delete
             * @return {Promise<BatchWriteItemOutput>} - Dynamo response for dynamoDB.BatchWriteItem
             */
            deleteItemsBySecondaryKeyFromDynamoDb(
                tableName: string,
                index: string,
                attribute: string,
                value: string,
            ): Chainable<Bluebird<DynamoDB.BatchWriteItemOutput>>;

            navigateToHomePage(): Chainable<void>;
            navigateToPatientSearchPage(): Chainable<void>;
            navigateToDownloadReportPage(): Chainable<void>;
        }
    }
}
