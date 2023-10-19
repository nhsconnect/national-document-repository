import authPayload from '../../fixtures/requests/auth/GET_TokenRequest.json';

describe('login functionality', () => {
    const baseUrl = 'http://localhost:3000';

    context('session management', () => {
        it('sets session storage on login and clears session storage on logout', () => {
            cy.login('gp');

            assertSessionStorage({
                auth: authPayload,
                isLoggedIn: true,
            });

            // Logout
            cy.intercept('GET', '/Auth/Logout', {
                statusCode: 200,
            }).as('logout');
            cy.getCy('logout-btn').click();
            cy.wait('@logout');

            assertSessionStorage({
                auth: null,
                isLoggedIn: false,
            });
        });

        const assertSessionStorage = (storage) => {
            cy.getAllSessionStorage().then((result) => {
                expect(result).to.deep.equal({
                    [baseUrl]: {
                        UserSession: JSON.stringify(storage),
                    },
                });
            });
        };
    });

    context('route access', () => {
        const unauthorisedRoutes = [
            '/search/patient',
            '/search/patient/result',
            '/search/results',
            '/search/patient/lloyd-george-record',
            '/search/upload',
            '/search/upload/result',
            '/upload/submit',
        ];

        unauthorisedRoutes.forEach((route) => {
            it('redirects logged-out user on unauthorised access to ' + route, () => {
                // Visit the unauthorised route
                cy.visit(baseUrl + route);

                // Assert that the user is redirected
                cy.url().should('equal', baseUrl + '/unauthorised');
            });
        });
    });
});
