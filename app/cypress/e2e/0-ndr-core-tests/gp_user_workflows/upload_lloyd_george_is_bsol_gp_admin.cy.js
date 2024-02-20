import { Roles } from '../../../support/roles';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatient.json';

const baseUrl = Cypress.config('baseUrl');
const searchPatientUrl = '/search/patient';
const clickUploadButton = () => {
    cy.get('#upload-button').click();
    cy.wait(20);
};

const uploadedFilePathNames = {
    LG: [
        'cypress/fixtures/lg-files/1of1_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        [
            'cypress/fixtures/lg-files/1of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
            'cypress/fixtures/lg-files/2of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        ],
    ],
};

const uploadedFileNames = {
    LG: [
        '1of1_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        [
            '1of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
            '2of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        ],
    ],
};
const bucketUrlIdentifer = 'document-store.s3.amazonaws.com';
const selectForm = () => cy.getByTestId(`upload-document-form`);
const singleFileUsecaseIndex = 0;
const multiFileUSecaseIndex = 1;

describe('GP Workflow: Upload Lloyd George record when user is GP amin and patient has no record', () => {
    const beforeEachConfiguration = () => {
        cy.login(Roles.GP_ADMIN);
        cy.visit(searchPatientUrl);

        cy.intercept('GET', '/SearchPatient*', {
            statusCode: 200,
            body: searchPatientPayload,
        }).as('search');
        cy.intercept('GET', '/LloydGeorgeStitch*', {
            statusCode: 404,
        }).as('stitch');

        cy.getByTestId('nhs-number-input').type(searchPatientPayload.nhsNumber);
        cy.getByTestId('search-submit-btn').click();
        cy.wait('@search');
        cy.get('#verify-submit').click();
        cy.wait('@stitch');
        cy.getByTestId('upload-patient-record-button').click();
    };

    beforeEach(() => {
        beforeEachConfiguration();
    });

    context('Upload Lloyd George document', () => {
        it(
            `GP ADMIN user can upload Lloyd George files for an active patient with no existing record`,
            { tags: 'regression' },
            () => {
                const fileName = uploadedFileNames.LG[0];

                const stubbedResponse = {
                    statusCode: 200,
                    body: {
                        [fileName]: {
                            url: 'http://' + bucketUrlIdentifer,
                            fields: {
                                key: 'test key',
                                'x-amz-algorithm': 'xxxx-xxxx-SHA256',
                                'x-amz-credential':
                                    'xxxxxxxxxxx/20230904/eu-west-2/s3/aws4_request',
                                'x-amz-date': '20230904T125954Z',
                                'x-amz-security-token': 'xxxxxxxxx',
                                'x-amz-signature': '9xxxxxxxx',
                            },
                        },
                    },
                };

                cy.url().should('include', 'upload');
                cy.url().should('eq', baseUrl + '/patient/upload/lloyd-george-record');
                cy.intercept('POST', '**/DocumentReference**', stubbedResponse);
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', {
                    statusCode: 204,
                });

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[singleFileUsecaseIndex],
                    { force: true },
                );
                clickUploadButton();
                cy.getByTestId('view-record-btn').should('be.visible');
                cy.getByTestId('search-patient-btn').should('be.visible');

                // cy.get('#upload-summary-confirmation').should('be.visible');
                // cy.get('#upload-summary-header').should('be.visible');
                // cy.get('#successful-uploads-dropdown').should('be.visible');
                // cy.get('#successful-uploads-dropdown').click();
                //
                // cy.get('#successful-uploads tbody tr').should('have.length', 1);
                //
                // cy.get('#successful-uploads tbody tr')
                //     .eq(1)
                //     .should('contain', uploadedFileNames.LG[singleFileUsecaseIndex]);
                // cy.get('#close-page-warning').should('be.visible');
            },
        );
    });
});
