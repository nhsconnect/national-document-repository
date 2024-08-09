import { Roles } from '../../../support/roles';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatientLGUpload.json';

const baseUrl = Cypress.config('baseUrl');
const patientSearchUrl = '/patient/search';
const patientVerifyUrl = '/patient/verify';
const lloydGeorgeViewUrl = '/patient/lloyd-george-record';
const lloydGeorgeUploadUrl = '/patient/lloyd-george-record/upload';
const lloydGeorgeInfectedUrl = '/patient/lloyd-george-record/upload/infected';
const arfDownloadUrl = '/patient/arf';
const arfUploadUrl = '/patient/arf/upload';
const unauthorisedUrl = '/unauthorised';

const clickUploadButton = () => {
    cy.get('#upload-button').click();
};

const testSearchPatientButton = () => {
    cy.getByTestId('search-patient-btn').should('be.visible');
    cy.getByTestId('search-patient-btn').click();
    cy.url().should('eq', baseUrl + patientSearchUrl);
};
const testViewRecordButton = () => {
    cy.getByTestId('view-record-btn').should('be.visible');
    cy.getByTestId('view-record-btn').click();
    cy.url().should('eq', baseUrl + lloydGeorgeViewUrl);
};

const testUploadCompletePageContent = () => {
    cy.getByTestId('upload-complete-card').should('be.visible');
    cy.getByTestId('view-record-btn').should('be.visible');
    cy.getByTestId('search-patient-btn').should('be.visible');
};

const uploadedFilePathNames = {
    LG: [
        'cypress/fixtures/lg-files/testy_test/1of1_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
        [
            'cypress/fixtures/lg-files/testy_test/1of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
            'cypress/fixtures/lg-files/testy_test/2of2_Lloyd_George_Record_[Testy Test]_[0123456789]_[01-01-2011].pdf',
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

const mockCreateDocRefHandler = (req) => {
    const uploadPayload = req.body.content[0].attachment;
    const clientIds = uploadPayload.map((document) => document.clientId);
    const responseBody = clientIds.reduce((body, id, currentIndex) => {
        body[id] = {
            url: 'http://' + bucketUrlIdentifer,
            fields: {
                key: `test key ${currentIndex}`,
                'x-amz-algorithm': 'xxxx-xxxx-SHA256',
                'x-amz-credential': 'xxxxxxxxxxx/20230904/eu-west-2/s3/aws4_request',
                'x-amz-date': '20230904T125954Z',
                'x-amz-security-token': 'xxxxxxxxx',
                'x-amz-signature': '9xxxxxxxx',
            },
        };
        return body;
    }, {});

    const response = { statusCode: 200, body: responseBody };

    req.reply(response);
};

describe('GP Workflow: Upload Lloyd George record when user is GP admin BSOL and patient has no record', () => {
    const beforeEachConfiguration = () => {
        cy.login(Roles.GP_ADMIN);
        cy.visit(patientSearchUrl);

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
        cy.url().should('eq', baseUrl + lloydGeorgeUploadUrl);
        cy.intercept('POST', '**/UploadState', (req) => {
            req.reply({
                statusCode: 200,
            });
        });
    };

    beforeEach(() => {
        beforeEachConfiguration();
    });

    context('Upload Lloyd George document for an active patient', () => {
        it(
            `User can upload a single LG file using the "Select files" button and can then view LG record`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', mockCreateDocRefHandler);
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                });
                cy.intercept('POST', '**/VirusScan', (req) => {
                    req.reply({
                        statusCode: 200,
                    });
                }).as('virus_scan');
                cy.intercept('POST', '**/UploadConfirm', (req) => {
                    req.reply({
                        statusCode: 204,
                    });
                }).as('upload_confirm');
                cy.title().should(
                    'eq',
                    'Upload a Lloyd George record - Access and store digital patient documents',
                );

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[singleFileUsecaseIndex],
                    { force: true },
                );
                clickUploadButton();

                cy.getByTestId('upload-documents-table').should(
                    'contain',
                    uploadedFileNames.LG[singleFileUsecaseIndex],
                );
                cy.wait('@upload_confirm');

                cy.getByTestId('upload-complete-page')
                    .should('include.text', 'Record uploaded for')
                    .should('include.text', 'You have successfully uploaded 1 file')
                    .should('include.text', 'Hide files')
                    .should('contain', uploadedFileNames.LG[singleFileUsecaseIndex]);

                testUploadCompletePageContent();
                cy.title().should(
                    'eq',
                    'Record upload complete - Access and store digital patient documents',
                );

                testViewRecordButton();
            },
        );

        it(
            `User can upload multiple LG files using the "Select files" button and can then view LG record`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', mockCreateDocRefHandler);
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                });
                cy.intercept('POST', '**/VirusScan', (req) => {
                    req.reply({
                        statusCode: 200,
                    });
                }).as('virus_scan');
                cy.intercept('POST', '**/UploadConfirm', (req) => {
                    req.reply({
                        statusCode: 204,
                    });
                }).as('upload_confirm');

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[multiFileUsecaseIndex],
                    { force: true },
                );
                clickUploadButton();
                cy.getByTestId('upload-documents-table')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);

                cy.wait('@upload_confirm');

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
                cy.intercept('POST', '**/DocumentReference**', mockCreateDocRefHandler);
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                });
                cy.intercept('POST', '**/VirusScan', (req) => {
                    req.reply({
                        statusCode: 200,
                    });
                }).as('virus_scan');
                cy.intercept('POST', '**/UploadConfirm', (req) => {
                    req.reply({
                        statusCode: 204,
                    });
                }).as('upload_confirm');

                cy.getByTestId('dropzone').selectFile(
                    uploadedFilePathNames.LG[multiFileUsecaseIndex],
                    { force: true, action: 'drag-drop' },
                );
                clickUploadButton();
                cy.getByTestId('upload-documents-table')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);

                cy.wait('@upload_confirm');

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
                cy.intercept('POST', '**/DocumentReference**', mockCreateDocRefHandler).as(
                    'doc_upload',
                );

                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 407,
                        delay: 1500,
                    });
                }).as('s3_upload');

                cy.intercept('POST', '**/VirusScan', (req) => {
                    req.reply({
                        statusCode: 200,
                    });
                }).as('virus_scan');

                cy.intercept('POST', '**/UploadConfirm', (req) => {
                    req.reply({
                        statusCode: 204,
                    });
                }).as('upload_confirm');

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[singleFileUsecaseIndex],
                    { force: true },
                );

                clickUploadButton();
                cy.wait('@doc_upload');
                cy.wait('@s3_upload');

                cy.getByTestId('retry-upload-error-box').should('exist');
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

                cy.getByTestId('error-box-link').should('exist');
                cy.getByTestId('error-box-link').click();

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
            `User can retry a multiple failed LG files using the "Retry all uploads" warning button and can then view LG record`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', mockCreateDocRefHandler).as(
                    'doc_upload',
                );
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 403,
                        delay: 1500,
                    });
                }).as('s3_upload');
                cy.intercept('POST', '**/VirusScan', (req) => {
                    req.reply({
                        statusCode: 200,
                    });
                }).as('virus_scan');
                cy.intercept('POST', '**/UploadConfirm', (req) => {
                    req.reply({
                        statusCode: 204,
                    });
                }).as('upload_confirm');

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[multiFileUsecaseIndex],
                    { force: true },
                );

                clickUploadButton();

                cy.wait('@doc_upload');
                cy.wait('@s3_upload');

                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 2500,
                    });
                }).as('s3_retry_upload');

                cy.getByTestId('upload-documents-table')
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][0])
                    .should('contain', uploadedFileNames.LG[multiFileUsecaseIndex][1]);

                cy.getByTestId('retry-upload-error-box').should('exist');

                cy.getByTestId('error-box-link').should('exist');
                cy.getByTestId('error-box-link').click();
                cy.wait('@s3_retry_upload');
                cy.wait('@upload_confirm');

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
                cy.intercept('POST', '**/DocumentReference**', mockCreateDocRefHandler).as(
                    'doc_upload',
                );
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 403,
                        delay: 1500,
                    });
                }).as('s3_upload');
                cy.intercept('POST', '**/VirusScan', (req) => {
                    req.reply({
                        statusCode: 200,
                    });
                }).as('virus_scan');
                cy.intercept('POST', '**/UploadConfirm', (req) => {
                    req.reply({
                        statusCode: 204,
                    });
                }).as('upload_confirm');

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

                cy.getByTestId('retry-upload-error-box').should('exist');

                cy.getByTestId('error-box-link').should('exist');
                cy.getByTestId('error-box-link').click();
                cy.wait('@s3_retry_upload');

                cy.get('#upload-retry-button').should('exist');
                cy.wait(1000);
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

        it(
            `User's upload journey is stopped if an infected file is detected`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', mockCreateDocRefHandler).as(
                    'doc_upload',
                );
                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 200,
                    });
                }).as('s3_upload');
                cy.intercept('POST', '**/VirusScan', (req) => {
                    req.reply({
                        statusCode: 500,
                    });
                }).as('virus_scan');

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[singleFileUsecaseIndex],
                    { force: true },
                );

                clickUploadButton();
                cy.wait('@doc_upload');
                cy.wait('@s3_upload');

                cy.getByTestId('failure-complete-page')
                    .should('include.text', 'Some of your files failed a virus scan')
                    .should('include.text', uploadedFileNames.LG[singleFileUsecaseIndex]);
                cy.title().should(
                    'eq',
                    'The record did not upload - Access and store digital patient documents',
                );
                cy.url().should('eq', baseUrl + lloydGeorgeInfectedUrl);

                cy.getByTestId('retry-upload-btn').should('exist');
                cy.getByTestId('retry-upload-btn').click();
                cy.url().should('eq', baseUrl + lloydGeorgeUploadUrl);
            },
        );

        it(
            `User is shown an error screen when the upload complete endpoint fails to complete`,
            { tags: 'regression' },
            () => {
                cy.intercept('POST', '**/DocumentReference**', mockCreateDocRefHandler).as(
                    'doc_upload',
                );

                cy.intercept('POST', '**/' + bucketUrlIdentifer + '**', (req) => {
                    req.reply({
                        statusCode: 204,
                        delay: 1500,
                    });
                }).as('s3_upload');
                cy.intercept('POST', '**/VirusScan', (req) => {
                    req.reply({
                        statusCode: 200,
                    });
                }).as('virus_scan');

                cy.intercept('POST', '**/UploadConfirm', (req) => {
                    req.reply({
                        statusCode: 500,
                    });
                }).as('upload_confirm');

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[singleFileUsecaseIndex],
                    { force: true },
                );

                clickUploadButton();
                cy.wait('@doc_upload');
                cy.wait('@s3_upload');

                cy.getByTestId('lloyd-george-upload-failed-panel').should('exist');
                cy.getByTestId('lloyd-george-upload-failed-panel').should(
                    'include.text',
                    'One or more files failed to upload, which prevented the full record being uploaded',
                );

                cy.getByTestId('retry-upload-btn').should('exist');
                cy.getByTestId('retry-upload-btn').click();
                cy.url().should('eq', baseUrl + lloydGeorgeUploadUrl);
            },
        );
        it(
            `It navigate to error page when uploading Lloyd George record is in progress for the patient`,
            { tags: 'regression' },
            () => {
                const stubbedResponse = {
                    statusCode: 423,
                    data: { err_code: 'LGL_423' },
                };

                cy.intercept('POST', '**/DocumentReference**', stubbedResponse);

                cy.getByTestId('button-input').selectFile(
                    uploadedFilePathNames.LG[singleFileUsecaseIndex],
                    { force: true },
                );
                clickUploadButton();
                cy.contains('Sorry, there is a problem with the service').should('be.visible');
            },
        );
    });
});
