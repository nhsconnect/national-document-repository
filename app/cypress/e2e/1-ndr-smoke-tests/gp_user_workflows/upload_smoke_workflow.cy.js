const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';
const gpRoles = ['GP_ADMIN', 'GP_CLINICAL'];

describe('GP Workflow: Upload docs and verify', () => {
    beforeEach(() => {
        cy.visit(baseUrl);
        process.env.REACT_APP_ENVIRONMENT = 'cypress';
    });
    gpRoles.forEach((role) => {
        it(`[Smoke] can navigate from Start page to Upload page as ${role}`, () => {
            cy.getByTestId('start-btn').click();
        });

        it(`[Smoke] can upload a single ARF or LG file, then renders 'Upload Summary' page for successful upload as ${role}`, () => {});
    });
});
