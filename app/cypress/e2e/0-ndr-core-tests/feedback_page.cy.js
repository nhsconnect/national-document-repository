const { Roles } = require('../../support/roles');

describe('Feedback Page', () => {
    const baseUrl = Cypress.config('baseUrl');
    const startUrl = '/';
    const feedbackUrl = '/feedback';

    const visitFeedbackPage = (role = Roles.GP_CLINICAL) => {
        cy.login(role);
        cy.visit(startUrl + feedbackUrl);
    };

    it(
        'opens the feedback page when the link at phase banner is clicked',
        { tags: 'regression' },
        () => {
            cy.visit(startUrl);

            cy.login(Roles.GP_CLINICAL);

            cy.get('.govuk-phase-banner__text').children('a').should('exist');
            cy.get('.govuk-phase-banner__text')
                .children('a')
                // for test purpose, remove "target=_blank" as cypress not supporting multiple tabs
                .invoke('removeAttr', 'target')
                .click();
            cy.url().should('contain', baseUrl + feedbackUrl);
        },
    );

    it('displays the correct page title on feedback page', { tags: 'regression' }, () => {
        visitFeedbackPage();

        cy.get('.app-homepage-content h1').should(
            'have.text',
            'Give feedback on accessing Lloyd George digital patient records',
        );
    });

    context('Submitting feedback', () => {
        it(
            'should display a confirmation screen after user has filled in and submitted the feedback form',
            { tags: 'regression' },
            () => {
                const mockInputData = {
                    feedbackContent: 'Some awesome feedback',
                    howSatisfied: 'Very satisfied',
                    respondentName: 'Jane Smith',
                    respondentEmail: 'jane_smith@fake-email-for-smoke-test.com',
                };

                visitFeedbackPage();

                cy.get('[data-testid=feedbackContent]').type(mockInputData.feedbackContent);
                cy.get(`.nhsuk-radios__item:has(label:contains(${mockInputData.howSatisfied}))`)
                    .find('input')
                    .click();
                cy.get('[data-testid=respondentName]').type(mockInputData.respondentName);
                cy.get('[data-testid=respondentEmail]').type(mockInputData.respondentEmail);

                cy.get('#submit-feedback').click();

                // TODO: intercept backend call for sending email and check that payload data is the same as mockInputData

                cy.get('#feedback-confirmation', { timeout: 5000 }).should('be.visible');
                cy.get('#feedback-confirmation').should(
                    'contain.text',
                    'We’ve received your feedback',
                );
            },
        );
    });
});
