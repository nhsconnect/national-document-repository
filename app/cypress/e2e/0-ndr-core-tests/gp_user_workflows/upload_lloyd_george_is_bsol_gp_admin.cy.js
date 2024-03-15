import { Roles } from '../../../support/roles';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatientLGUpload.json';

const baseUrl = Cypress.config('baseUrl');
const searchPatientUrl = '/search/patient';
const viewLloydGeorgeRecordUrl = '/patient/view/lloyd-george-record';
const clickUploadButton = () => {
    cy.get('#upload-button').click();
};

const testSearchPatientButton = () => {
    cy.getByTestId('search-patient-btn').should('be.visible');
    cy.getByTestId('search-patient-btn').click();
    cy.url().should('eq', baseUrl + searchPatientUrl);
};
const testViewRecordButton = () => {
    cy.getByTestId('view-record-btn').should('be.visible');
    cy.getByTestId('view-record-btn').click();
    cy.url().should('eq', baseUrl + viewLloydGeorgeRecordUrl);
};

const testUploadCompletePageContent = () => {
    cy.getByTestId('upload-complete-card').should('be.visible');
    cy.getByTestId('view-record-btn').should('be.visible');
    cy.getByTestId('search-patient-btn').should('be.visible');
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
const singleFileUsecaseIndex = 0;
const multiFileUsecaseIndex = 1;
const fileNames = uploadedFileNames.LG[multiFileUsecaseIndex];

const stubbedResponseMulti = {
    statusCode: 200,
    body: {
        [fileNames[0]]: {
            url: 'http://' + bucketUrlIdentifer,
            fields: {
                key: 'test key',
                'x-amz-algorithm': 'xxxx-xxxx-SHA256',
                'x-amz-credential': 'xxxxxxxxxxx/20230904/eu-west-2/s3/aws4_request',
                'x-amz-date': '20230904T125954Z',
                'x-amz-security-token': 'xxxxxxxxx',
                'x-amz-signature': '9xxxxxxxx',
            },
        },
        [fileNames[1]]: {
            url: 'http://' + bucketUrlIdentifer,
            fields: {
                key: 'test key',
                'x-amz-algorithm': 'xxxx-xxxx-SHA256',
                'x-amz-credential': 'xxxxxxxxxxx/20230904/eu-west-2/s3/aws4_request',
                'x-amz-date': '20230904T125954Z',
                'x-amz-security-token': 'xxxxxxxxx',
                'x-amz-signature': '9xxxxxxxx',
            },
        },
    },
};
describe('GP Workflow: Upload Lloyd George record when user is GP admin BSOL and patient has no record', () => {
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
        cy.url().should('include', 'upload');
        cy.url().should('eq', baseUrl + '/patient/upload/lloyd-george-record');
    };

    beforeEach(() => {
        beforeEachConfiguration();
    });

    context('Upload Lloyd George document for an active patient', () => {
        it(
            `User can upload a single LG file using the "Select files" button and can then view LG record`,
            { tags: 'regression' },
            () => {
                const fileName = uploadedFileNames.LG[singleFileUsecaseIndex];

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

                cy.intercept('POST', '**/DocumentReference**', stubbedResponse);
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                });

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[singleFileUsecaseIndex],
                    { force: true },
                );
                clickUploadButton();

                cy.getByTestId('upload-documents-table').should(
                    'contain',
                    uploadedFileNames.LG[singleFileUsecaseIndex],
                );
                cy.wait(20);

                cy.getByTestId('upload-complete-page')
                    .should('include.text', 'Record uploaded for')
                    .should('include.text', 'You have successfully uploaded 1 file')
                    .should('include.text', 'Hide files')
                    .should('contain', uploadedFileNames.LG[singleFileUsecaseIndex]);

                testUploadCompletePageContent();

                testViewRecordButton();
            },
        );
        it(
            `User can upload a multiple LG file using the "Select files" button and can then view LG record`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', stubbedResponseMulti);
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                });

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[multiFileUsecaseIndex],
                    { force: true },
                );
                clickUploadButton();
                cy.getByTestId('upload-documents-table')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);

                cy.getByTestId('upload-complete-page')
                    .should('include.text', 'Record uploaded for')
                    .should('include.text', 'You have successfully uploaded 2 files')
                    .should('include.text', 'Hide files');

                testUploadCompletePageContent();

                testSearchPatientButton();
            },
        );

        it(
            `User can upload a multiple LG file using drag and drop and can then view LG record`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', stubbedResponseMulti);
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                });

                cy.getByTestId('dropzone').selectFile(
                    uploadedFilePathNames.LG[multiFileUsecaseIndex],
                    { force: true, action: 'drag-drop' },
                );
                clickUploadButton();
                cy.getByTestId('upload-documents-table')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);

                cy.getByTestId('upload-complete-page')
                    .should('include.text', 'Record uploaded for')
                    .should('include.text', 'You have successfully uploaded 2 files')
                    .should('include.text', 'Hide files')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);
                testUploadCompletePageContent();

                testSearchPatientButton();
            },
        );

        it(
            `User can retry failed upload with a single LG file using the "Retry upload" button and can then view LG record`,
            { tags: 'regression' },
            () => {
                const fileName = uploadedFileNames.LG[singleFileUsecaseIndex];

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

                cy.intercept('POST', '**/DocumentReference**', stubbedResponse).as('doc_upload');

                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 403,
                        delay: 1500,
                    });
                }).as('s3_upload');

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[singleFileUsecaseIndex],
                    { force: true },
                );

                clickUploadButton();
                cy.wait('@doc_upload');
                cy.wait('@s3_upload');

                cy.getByTestId('retry-upload-btn').should('exist');
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                }).as('s3_retry_upload');

                cy.getByTestId('upload-documents-table').should(
                    'contain',
                    uploadedFileNames.LG[singleFileUsecaseIndex],
                );

                cy.getByTestId('retry-upload-btn').click();
                cy.wait('@s3_retry_upload');

                cy.getByTestId('upload-complete-page')
                    .should('include.text', 'Record uploaded for')
                    .should('include.text', 'You have successfully uploaded 1 file')
                    .should('include.text', 'Hide files')
                    .should('contain', uploadedFileNames.LG[singleFileUsecaseIndex]);

                testUploadCompletePageContent();

                testViewRecordButton();
            },
        );

        it(
            `User can retry a multiple failed LG files using the "Retry all uploads"CTA button and can then view LG record`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', stubbedResponseMulti).as(
                    'doc_upload',
                );
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 403,
                        delay: 1500,
                    });
                }).as('s3_upload');

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[multiFileUsecaseIndex],
                    { force: true },
                );

                clickUploadButton();
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 2500,
                    });
                }).as('s3_retry_upload');
                cy.wait('@doc_upload');
                cy.wait('@s3_upload');
                cy.getByTestId('upload-documents-table')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);
                cy.getByTestId('error-summary-btn').should('exist');

                cy.getByTestId('error-summary-btn').click();
                cy.wait('@s3_retry_upload');

                cy.getByTestId('upload-complete-page')
                    .should('include.text', 'Record uploaded for')
                    .should('include.text', 'You have successfully uploaded 2 files')
                    .should('include.text', 'Hide files')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);
                testUploadCompletePageContent();

                testSearchPatientButton();
            },
        );

        it(
            `User can restart upload LG files journey when document upload fails more than once`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', stubbedResponseMulti).as(
                    'doc_upload',
                );
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 403,
                        delay: 1500,
                    });
                }).as('s3_upload');

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[multiFileUsecaseIndex],
                    { force: true },
                );

                clickUploadButton();
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 403,
                        delay: 2500,
                    });
                }).as('s3_retry_upload');
                cy.wait('@doc_upload');
                cy.wait('@s3_upload');
                cy.getByTestId('upload-documents-table')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);
                cy.getByTestId('error-summary-btn').should('exist');

                cy.getByTestId('error-summary-btn').click();
                cy.wait('@s3_retry_upload');

                cy.get('#upload-retry-button').should('exist');

                cy.get('#upload-retry-button').click();
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                }).as('retry_success');
                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[multiFileUsecaseIndex],
                    { force: true },
                );

                clickUploadButton();

                cy.wait('@retry_success');
                cy.getByTestId('upload-complete-page')
                    .should('include.text', 'Record uploaded for')
                    .should('include.text', 'You have successfully uploaded 2 files')
                    .should('include.text', 'Hide files')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);
                testUploadCompletePageContent();

                testViewRecordButton();
            },
        );
    });
});
