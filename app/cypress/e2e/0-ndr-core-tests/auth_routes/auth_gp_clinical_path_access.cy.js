import { Roles } from '../../../support/roles';
import { routes } from '../../../support/routes';

const testPatient = '9000000009';
const patient = {
    birthDate: '1970-01-01',
    familyName: 'Default Surname',
    givenName: ['Default Given Name'],
    nhsNumber: testPatient,
    postalCode: 'AA1 1AA',
    superseded: false,
    restricted: false,
    active: true,
    deceased: false,
};

const baseUrl = Cypress.config('baseUrl');
const patientVerifyUrl = '/patient/verify';
const lloydGeorgeViewUrl = '/patient/lloyd-george-record';
const arfDownloadUrl = '/patient/arf';
const forbiddenRoutes = [arfDownloadUrl];

describe('GP Clinical user role has access to the expected GP_CLINICAL workflow paths', () => {
    context(`GP Clinical role has access to expected routes`, () => {
        it('GP Clinical role has access to Lloyd George View', { tags: 'regression' }, () => {
            cy.intercept('GET', '/SearchPatient*', {
                statusCode: 200,
                body: patient,
            }).as('search');

            cy.login(Roles.GP_CLINICAL);

            cy.url().should('eq', baseUrl + routes.home);

            cy.navigateToPatientSearchPage();

            cy.url().should('eq', baseUrl + routes.patientSearch);

            cy.get('#nhs-number-input').click();
            cy.get('#nhs-number-input').type(testPatient);
            cy.get('#search-submit').click();
            cy.wait('@search');

            cy.url().should('include', 'verify');
            cy.url().should('eq', baseUrl + patientVerifyUrl);

            cy.get('#verify-submit').click();

            cy.url().should('include', 'lloyd-george-record');
            cy.url().should('eq', baseUrl + lloydGeorgeViewUrl);
        });
    });
});

describe('GP Clinical user role cannot access expected forbidden routes', () => {
    context('GP Clinical role has no access to forbidden routes', () => {
        forbiddenRoutes.forEach((forbiddenRoute) => {
            it(
                'GP Clinical role cannot access route ' + forbiddenRoute,
                { tags: 'regression' },
                () => {
                    cy.login(Roles.GP_CLINICAL);
                    cy.visit(forbiddenRoute);
                    cy.url().should('include', 'unauthorised');
                },
            );
        });
    });
});
