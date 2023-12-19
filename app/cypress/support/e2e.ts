/// <reference types="cypress" />
// ***********************************************************
// This example support/e2e.ts is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

import './commands';
import './aws.commands';

Cypress.Commands.add('getByTestId', (selector, ...args) => {
    return cy.get(`[data-testid=${selector}]`, ...args);
});

Cypress.Commands.add('login', (role) => {
    if (role === 'GP_ADMIN' || role === 'GP_CLINICAL' || role === 'PCSE') {
        const baseUrl = Cypress.config('baseUrl');

        // login and navigate to search
        cy.intercept('GET', '/Auth/TokenRequest*', {
            statusCode: 200,
            fixture: 'requests/auth/GET_TokenRequest_' + role + '.json',
        }).as('auth');
        cy.visit(baseUrl + '/auth-callback');
        cy.wait('@auth');
    } else {
        throw new Error("Invalid role for login. Only 'gp' or 'pcse' are allowed.");
    }
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
            getByTestId(value: string): Chainable<Subject>;
            /**
             * Mock user login via CIS2 and return to base URL.
             * @param {string} role - The user role to login with. Must be either 'gp' or 'pcse'
             */
            login(role: string): Chainable<Subject>;
            /**
             * Add file to s3 bucket
             * @param {string} bucketName - Name of the target S3 bucket
             * @param {string} fileName - Filepath of the file to upload
             * @param {string} fileContent - Content of the file to upload
             */
            addFileToS3(
                bucketName: string,
                fileName: string,
                fileContent: string,
            ): Chainable<Subject>;
            /**
             * Add dynamoDB entry
             * @param {string} tableName - Name of the target dynamoDB table
             * @param {{ [key: string]: any; }} item - dynamoDB item to upload
             */
            addItemToDynamoDb(
                tableName: string,
                item: { [key: string]: string },
            ): Chainable<Subject>;
            /**
             * Delete file from S3 bucket
             * @param {string} bucketName - Name of the target S3 bucket
             * @param {string} fileName - Filepath of the file to delete
             */
            deleteFileFromS3(bucketName: string, fileName: string): Chainable<Subject>;
            /**
             * Delete item from DynamoDB table
             * @param {string} tableName - Name of the target DynamoDB table
             * @param {string} itemId - ID of the item to delete
             */
            deleteItemFromDynamoDb(tableName: string, itemId: string): Chainable<Subject>;
        }
    }
}
