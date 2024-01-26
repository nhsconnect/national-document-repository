import { DynamoDB, S3 } from 'aws-sdk';
import { Roles, roleIds, roleList } from './roles';
import Bluebird from 'cypress/types/bluebird';
import './aws.commands';

/// <reference types="cypress" />
const registerCypressGrep = require('@cypress/grep');
registerCypressGrep();

Cypress.Commands.add('getByTestId', (selector, ...args) => {
    return cy.get(`[data-testid=${selector}]`, ...args);
});

Cypress.Commands.add('login', (role, isBSOL = true) => {
    if (roleIds.includes(role)) {
        const roleName = roleList.find((roleName) => Roles[roleName] === role);
        // Login for regression tests
        const authCallback = '/auth-callback';
        const fixturePath =
            [Roles.GP_ADMIN, Roles.GP_CLINICAL].includes(role) && !isBSOL
                ? 'requests/auth/GET_TokenRequest_' + roleName + '_non_bsol.json'
                : 'requests/auth/GET_TokenRequest_' + roleName + '.json';

        cy.intercept('GET', '/Auth/TokenRequest*', {
            statusCode: 200,
            fixture: fixturePath,
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

        const startUrl = '/';
        const homeUrl = '/home';
        const authCallback = '/auth-callback';
        cy.visit(startUrl);
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
        cy.url({ timeout: 10000 }).should('contain', baseUrl + homeUrl);
    } else {
        throw new Error("Invalid role for login. Only 'gp' or 'pcse' are allowed.");
    }
});

Cypress.Commands.add('downloadIframeReplace', () => {
    cy.window().then((win) => {
        const triggerAutIframeLoad = () => {
            const AUT_IFRAME_SELECTOR = '.aut-iframe';

            // get the application iframe
            const autIframe = win.parent.document.querySelector(AUT_IFRAME_SELECTOR);

            if (!autIframe) {
                throw new ReferenceError(
                    `Failed to get the application frame using the selector '${AUT_IFRAME_SELECTOR}'`,
                );
            }

            autIframe.dispatchEvent(new Event('load'));
            // remove the event listener to prevent it from firing the load event before each next unload
            win.removeEventListener('beforeunload', triggerAutIframeLoad);
        };

        win.addEventListener('beforeunload', triggerAutIframeLoad);
    });
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
             * @param {boolean} isBSOL - Whether the user GP is located in BSOL area
             */
            login(role: Roles, isBSOL?: boolean): Chainable<void>;

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
             * Workaround to prevent click on download link from firing a load event and preventing test continuing to run
             */
            downloadIframeReplace(): Chainable<void>;
        }
    }
}
