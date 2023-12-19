describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const username = Cypress.env('USERNAME') ?? 'test';
    const password = Cypress.env('PASSWORD');
    const homeUrl = '/';

    beforeEach(() => {
        cy.visit(homeUrl);
    });

    it('[Smoke] should visit expected URL', { tags: 'smoke' }, () => {
        cy.url().should('eq', baseUrl + homeUrl);
    });

    context('Login tests', () => {
        it('displays expected page header on home page when logged in', { tags: 'smoke' }, () => {
            // Add CIS2 login steps
            cy.get('header').should('have.length', 1);

            cy.get('.nhsuk-logo__background').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name').children().should('have.length', 1);
            cy.get('.nhsuk-header__transactional-service-name--link').should(
                'have.text',
                'Access and store digital GP records',
            );

            cy.getByTestId('start-btn').should('exist');
            cy.getByTestId('start-btn').click();
            cy.origin(
                'https://am.nhsdev.auth-ptl.cis2.spineservices.nhs.uk',
                { args: { username, password } },
                (args) => {
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
                },
            );

            // Restore once login steps implemented
            // cy.get('.nhsuk-header__navigation').should('have.length', 1);
            // cy.get('.nhsuk-header__navigation-list').should('have.length', 1);
        });
    });
});
