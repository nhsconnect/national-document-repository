import { Roles } from '../../support/roles';
import { errorCodes } from '../../../src/helpers/utils/errorCodes';
const baseUrl = Cypress.config('baseUrl');

describe('Confirm Error Code Messages', () => {
    const searchPatientUrl = '/search/patient';

    console.log(errorCodes);
    // errorCodes.keys().forEach((error) => {
    //     beforeEach(() => {
    //         cy.login(Roles.GP_ADMIN);
    //         cy.visit(searchPatientUrl);
    //     });

    //     it(`Error code ${error} displays correct error message`, { tags: 'regression' }, () => {
    //         cy.intercept('GET', '/SearchPatient*', {
    //             statusCode: 500,
    //             message: "Not relevant",
    //             err_code: error,
    //             interaction_id: "101010"
    //         }).as('search');

    //         cy.get('#nhs-number-input').click();
    //         cy.get('#nhs-number-input').type(testPatient);

    //         cy.get('#search-submit').click();
    //         cy.wait('@search');

    //         cy.getByTestId('error-displayed-message').should('eq', errorCodes[error]);
    //     });
    // });
});
