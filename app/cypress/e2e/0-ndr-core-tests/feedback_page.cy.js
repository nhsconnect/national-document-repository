const { Roles } = require('../../support/roles');
const searchPatientPayload = require('../../fixtures/requests/GET_SearchPatient.json');

describe('Home Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const startUrl = '/';
    const feedbackUrl = '/feedback';

    const visitFeedbackPage = (role = Roles.GP_CLINICAL) => {
        cy.login(role);
        cy.visit(startUrl + feedbackUrl);
    };

    // beforeEach(() => {
    //
    // });
    it(
        'Open a feedback page when the link at phase banner is clicked',
        { tags: 'regression' },
        () => {
            cy.visit(startUrl);

            cy.login(Roles.GP_CLINICAL);

            cy.get('.govuk-phase-banner__text').children('a').should('exist');
            cy.get('.govuk-phase-banner__text')
                .children('a')
                // remove target = _blank as cypress does not support multiple tabs
                .invoke('removeAttr', 'target')
                .click();
            cy.url({ timeout: 10000 }).should('contain', baseUrl + feedbackUrl);
        },
    );

    it('Fill in and submit feedback form', { tags: 'regression' }, () => {
        visitFeedbackPage();

        cy.get('[data-testid=feedbackContent]').type('');
    });
});
