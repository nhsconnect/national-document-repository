describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const username = Cypress.env('USERNAME');
    const password = Cypress.env('PASSWORD');
    const homeUrl = '/';
    const authCallback = '/auth-callback';
    const searchUrl = '/search/upload';
    beforeEach(() => {
        cy.visit(homeUrl);
    });

    it('[Smoke] should visit expected URL', { tags: 'smoke' }, () => {
        cy.url().should('eq', baseUrl + homeUrl);
    });

    it('[Smoke] should display patient search page after user log in', { tags: 'smoke' }, () => {
        // Add CIS2 login steps
        cy.get('header').should('have.length', 1);

        cy.get('.nhsuk-logo__background').should('have.length', 1);
        cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
        cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
        cy.get('.nhsuk-header__transactional-service-name--link').should(
            'have.text',
            'Access and store digital GP records',
        );
        cy.get('.nhsuk-header__navigation').should('not.exist');
        cy.get('.nhsuk-header__navigation-list').should('not.exist');

        cy.getByTestId('start-btn').should('exist');
        cy.getByTestId('start-btn').click();
        cy.origin(
            'https://am.nhsdev.auth-ptl.cis2.spineservices.nhs.uk',
            { args: { username, password } },
            (args) => {
                Cypress.on('uncaught:exception', () => false);
                const practitionerRoleId = 555053929106;
                const { username, password } = args;
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
                cy.get(`#nhsRoleId_${practitionerRoleId}`).should('exist');
                cy.get(`#nhsRoleId_${practitionerRoleId}`).click();
            },
        );
        cy.url().should('contain', baseUrl + authCallback);
        cy.url({ timeout: 10000 }).should('eq', baseUrl + searchUrl);

        cy.get('.nhsuk-header__navigation').should('exist');
        cy.get('.nhsuk-header__navigation-list').should('exist');
    });
});
