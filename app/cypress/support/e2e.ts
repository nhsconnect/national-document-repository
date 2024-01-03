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
import { Roles, roleIds, roleList } from './roles';

Cypress.Commands.add('getByTestId', (selector, ...args) => {
    return cy.get(`[data-testid=${selector}]`, ...args);
});

Cypress.Commands.add('login', (role) => {
    if (roleIds.includes(role)) {
        const roleName = roleList.find((roleName) => Roles[roleName] === role);
        // Login for regression tests
        const authCallback = '/auth-callback';
        cy.intercept('GET', '/Auth/TokenRequest*', {
            statusCode: 200,
            fixture: 'requests/auth/GET_TokenRequest_' + roleName + '.json',
        }).as('auth');
        cy.visit(authCallback);
        cy.wait('@auth');
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
        const homeUrl = '/';
        const authCallback = '/auth-callback';
        const searchUrl = '/search';
        cy.visit(homeUrl);
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
                cy.get('.nhsuk-cis2-cia-header-text').should(
                    'have.text',
                    'CIS2 - Care Identity Authentication',
                );
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
        cy.url().should('contain', baseUrl + authCallback);
        cy.url({ timeout: 10000 }).should('contain', baseUrl + searchUrl);
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
            getByTestId(value: string);
            /**
             * Mock user login by intercepting the {baseUrl}/auth-callback request
             * @param {Roles} role - The user role to login with. Must be an enum of Roles
             */
            login(role: Roles);
            /**
             * Real user login via CIS2 and redirect back to {baseUrl}/auth-callback.
             * @param {Roles} role - The user role to login with. Must be an enum of Roles
             */
            smokeLogin(role: Roles);
            /**
             * Add file to s3 bucket
             * @param {string} bucketName - Name of the target S3 bucket
             * @param {string} fileName - Filepath of the file to upload
             * @param {string} fileContent - Content of the file to upload
             */
            addFileToS3(bucketName: string, fileName: string, fileContent: AWS.S3.Body);
            /**
             * Add dynamoDB entry
             * @param {string} tableName - Name of the target dynamoDB table
             * @param {{ [key: string]: any; }} item - dynamoDB item to upload
             */
            addItemToDynamoDb(tableName: string, item: AWS.DynamoDB.PutItemInputAttributeMap);
            /**
             * Delete file from S3 bucket
             * @param {string} bucketName - Name of the target S3 bucket
             * @param {string} fileName - Filepath of the file to delete
             */
            deleteFileFromS3(bucketName: string, fileName: string);
            /**
             * Delete item from DynamoDB table
             * @param {string} tableName - Name of the target DynamoDB table
             * @param {string} itemId - ID of the item to delete
             */
            deleteItemFromDynamoDb(tableName: string, itemId: string);
        }
    }
}
