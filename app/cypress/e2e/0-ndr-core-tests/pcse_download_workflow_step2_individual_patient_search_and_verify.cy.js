// pcse_all_worflows_step1_individual_patient_search is the first step in this workflow

describe('PCSE Download Workflow: Access and download found files', () => {
    // env vars
    const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';
    const smokeTest = Cypress.env('CYPRESS_RUN_AS_SMOKETEST') ?? false;

    const roles = Object.freeze({
        GP: 'gp',
        PCSE: 'pcse',
    });

    const testPatient = '9000000009';
    const patient = {
        birthDate: new Date('1970-01-01'),
        familyName: 'Default Surname',
        givenName: ['Default Given Name'],
        nhsNumber: testPatient,
        postalCode: 'AA1 1AA',
        superseded: false,
        restricted: false,
    };

    const searchDocumentReferencesResponse = [
        {
            fileName: 'Screenshot 2023-09-11 at 16.06.40.png',
            virusScannerResult: 'Not Scanned',
            created: new Date('2023-09-12T10:41:41.747836Z'),
        },
        {
            fileName: 'Screenshot 2023-09-08 at 14.53.47.png',
            virusScannerResult: 'Not Scanned',
            created: new Date('2023-09-12T10:41:41.749341Z'),
        },
    ];

    beforeEach(() => {
        cy.visit(baseUrl);
    });

    const navigateToVerify = (role) => {
        cy.visit(baseUrl + 'auth-callback');
        cy.intercept('GET', '/Auth/TokenRequest*', {
            statusCode: 200,
            body: {
                organisations: [
                    {
                        org_name: 'PORTWAY LIFESTYLE CENTRE',
                        ods_code: 'A470',
                        role: 'DEV',
                    },
                ],
                authorisation_token: '111xxx222',
            },
        }).as('auth');
        cy.intercept('GET', '/SearchPatient*', {
            statusCode: 200,
            body: patient,
        }).as('search');
        cy.wait('@auth');
        cy.get(`#${role}-radio-button`).click();
        cy.get('#role-submit-button').click();
        cy.get('#nhs-number-input').click();
        cy.get('#nhs-number-input').type(testPatient);
        cy.get('#search-submit').click();
        cy.wait('@search');
    };

    const navigateToDownload = (role) => {
        navigateToVerify(role);
        cy.get('#verify-submit').click();
    };

    it('(Smoke test) shows patient details on download page', () => {
        navigateToDownload(roles.PCSE);

        cy.get('#download-page-title').should('have.length', 1);
        cy.get('#patient-summary-nhs-number').should('have.text', patient.nhsNumber);
        cy.get('#patient-summary-family-name').should('have.text', patient.familyName);

        const givenName = patient.givenName[0];
        cy.get('#patient-summary-given-name').should('have.text', givenName);
        cy.get('#patient-summary-date-of-birth').should(
            'have.text',
            patient.birthDate.toLocaleDateString('en-GB', {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
            })
        );
        cy.get('#patient-summary-postcode').should('have.text', patient.postalCode);
    });

    it('(Smoke test) shows no files avaliable on 204 success', () => {
        const searchDocumentReferencesResponse = [];

        cy.intercept('GET', '/SearchDocumentReferences*', {
            statusCode: 204,
            body: searchDocumentReferencesResponse,
        }).as('search');

        navigateToDownload(roles.PCSE);

        cy.get('#no-files-message').should('have.length', 1);
        cy.get('#no-files-message').should(
            'have.text',
            'There are no documents available for this patient.'
        );
    });

    it('(Smoke test) shows avaliable files to download on 200 success', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchDocumentReferences*', {
                statusCode: 200,
                body: searchDocumentReferencesResponse,
            }).as('search');
        }

        navigateToDownload(roles.PCSE);

        cy.get('#available-files-table-title').should('have.length', 1);

        cy.get('.available-files-row').should('have.length', 2);
        cy.get('#available-files-row-0-filename').should(
            'have.text',
            searchDocumentReferencesResponse[1].fileName
        );
        cy.get('#available-files-row-1-filename').should(
            'have.text',
            searchDocumentReferencesResponse[0].fileName
        );

        cy.get('#available-files-row-0-created-date').should('exist');
        cy.get('#available-files-row-1-created-date').should('exist');

        // We cannot test datetimes of a created s3 bucket object easily on a live instance, therefore
        // the exists checks above should be enough for a smoketest

        if (!smokeTest) {
            cy.get('#available-files-row-0-created-date').should(
                'have.text',
                searchDocumentReferencesResponse[1].created.toLocaleDateString('en-GB', {
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric',
                    hour: 'numeric',
                    minute: 'numeric',
                    second: 'numeric',
                })
            );
            cy.get('#available-files-row-1-created-date').should(
                'have.text',
                searchDocumentReferencesResponse[0].created.toLocaleDateString('en-GB', {
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric',
                    hour: 'numeric',
                    minute: 'numeric',
                    second: 'numeric',
                })
            );
        }
    });

    it('Shows spinner button while waiting for Download Document Manifest response', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchDocumentReferences*', {
                statusCode: 200,
                body: searchDocumentReferencesResponse,
            }).as('search');
        }

        navigateToDownload(roles.PCSE);

        const documentManifestResponse = 'test-s3-url';

        cy.get('#download-documents').click();

        cy.intercept({ url: '/DocumentManifest*', middleware: true }, (req) => {
            req.reply({
                statusCode: 200,
                body: documentManifestResponse,
                delay: 1500,
            });
        }).as('search');

        cy.get('#download-spinner').should('exist');
    });

    it('Downloads file from the correct s3 url during Download Document Manifest', () => {
        if (!smokeTest) {
            cy.intercept('GET', '/SearchDocumentReferences*', {
                statusCode: 200,
                body: searchDocumentReferencesResponse,
            }).as('search');
        }

        navigateToDownload(roles.PCSE);

        const documentManifestResponse = 'test-s3-url';

        cy.get('#download-link').invoke('attr', 'href').should('eq', '');
        cy.get('#download-link').invoke('attr', 'download').should('eq', '');

        cy.get('#download-documents').click();

        cy.intercept({ url: '/DocumentManifest*', middleware: true }, (req) => {
            req.reply({
                statusCode: 200,
                body: documentManifestResponse,
            });
        }).as('search');

        cy.get('#download-link').invoke('attr', 'href').should('eq', 'test-s3-url');
        cy.get('#download-link')
            .invoke('attr', 'download')
            .should('eq', `patient-record-${testPatient}`);
    });

    it('Shows service error box on Search Document Reference 500 response', () => {
        cy.intercept('GET', '/SearchDocumentReferences*', {
            statusCode: 500,
        }).as('search');

        navigateToDownload(roles.PCSE);

        cy.get('#service-error').should('exist');
    });

    it('Shows progress bar while waiting for Search Document Reference response', () => {
        const searchDocumentReferencesResponse = [];

        cy.intercept({ url: '/SearchDocumentReferences*', middleware: true }, (req) => {
            req.reply({
                statusCode: 204,
                body: searchDocumentReferencesResponse,
                delay: 1500,
            });
        }).as('search');

        navigateToDownload(roles.PCSE);

        cy.get('.progress-bar').should('exist');
    });

    it('Start again button takes us to the home page', () => {
        const searchDocumentReferencesResponse = [];

        cy.intercept({ url: '/SearchDocumentReferences*', middleware: true }, (req) => {
            req.reply({
                statusCode: 204,
                body: searchDocumentReferencesResponse,
            });
        }).as('search');

        navigateToDownload(roles.PCSE);

        cy.get('#start-again-link').should('exist');
        cy.get('#start-again-link').click();
        cy.url().should('eq', baseUrl);
    });
});
