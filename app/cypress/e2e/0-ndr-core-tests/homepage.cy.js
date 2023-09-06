/// <reference types="cypress" />

// Welcome to Cypress!
//
// This spec file contains a variety of sample tests
// for a todo list app that are designed to demonstrate
// the power of writing tests in Cypress.
//
// To learn more about how Cypress works and
// what makes it such an awesome testing tool,
// please read our getting started guide:
// https://on.cypress.io/introduction-to-cypress

describe('Home Page Tests', () => {
    const baseUrl = 'http://localhost:3000/';
    const smokeTest = false;

    beforeEach(() => {
        // Cypress starts out with a blank slate for each test
        // so we must tell it to visit our website with the `cy.visit()` command.
        // Since we want to visit the same URL at the start of all our tests,
        // we include it in our beforeEach function so that it runs before each test
        cy.visit(baseUrl);
    });

    it('Test expected URL is correct', () => {
        //ensure the page header is visable
        cy.url().should('eq', 'http://localhost:3000/');
    });

    it('displays expected page header on home page', () => {
        //ensure the page header is visable
        cy.get('header').should('have.length', 1);

        cy.get('.nhsuk-logo__background').should('have.length', 1);
        cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
        cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
        cy.get('.nhsuk-header__transactional-service-name--link').should(
            'have.text',
            'Inactive Patient Record Administration',
        );

        cy.get('.nhsuk-header__navigation').should('have.length', 1);
        cy.get('.nhsuk-header__navigation-list').should('have.length', 1);
    });

    it('displays correct page title on home page', () => {
        //ensure the page header is visable
        cy.get('.app-homepage-content h1').should(
            'have.text',
            'Inactive Patient Record Administration',
        );
    });

    it('displays start now button on home page', () => {
        //ensure the page header is visable
        cy.get('.nhsuk-button').should('have.text', 'Start now');
    });

    it('On Start now button click, redirect to uploads is successful', () => {
        //ensure the page header is visable
        cy.get('.nhsuk-button').click();
        cy.wait(20);
        cy.url().should('include', 'organisation');
        cy.url().should('eq', 'http://localhost:3000/select-organisation');
    });
});
