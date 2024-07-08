import viewLloydGeorgePayload from '../../../fixtures/requests/GET_LloydGeorgeStitch.json';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatient.json';
import { Roles, roleName } from '../../../support/roles';
import { formatNhsNumber } from '../../../../src/helpers/utils/formatNhsNumber';

const baseUrl = Cypress.config('baseUrl');
const gpRoles = [Roles.GP_ADMIN];

describe('GP Workflow: View Lloyd George record', () => {
    const assertEmptyLloydGeorgeCard = () => {
        cy.getByTestId('pdf-card').should('include.text', 'Lloyd George record');
        cy.getByTestId('pdf-card').should('include.text', 'No documents are available');
    };

    const assertFailedLloydGeorgeLoad = () => {
        cy.getByTestId('error-summary_message').should(
            'include.text',
            'An error has occurred when creating the Lloyd George preview.',
        );
    };

    const assertTimeoutLloydGeorgeError = (assertDownloadLink) => {
        cy.getByTestId('lloyd-george-record-error-message').should(
            'include.text',
            'The Lloyd George document is too large to view in a browser,',
        );

        if (assertDownloadLink) {
            cy.getByTestId('download-instead-link').should('exist');
        } else {
            cy.getByTestId('download-instead-link').should('exist');
            cy.getByTestId('download-instead-link').click();
            cy.url().should('contains', baseUrl + '/unauthorised');
        }
    };

    const assertPatientInfo = () => {
        cy.getByTestId('patient-name').should(
            'have.text',
            `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
        );
        cy.getByTestId('patient-nhs-number').should('have.text', `NHS number: 900 000 0009`);
        cy.getByTestId('patient-dob').should('have.text', `Date of birth: 01 January 1970`);
    };

    const beforeEachConfiguration = (role) => {
        const isBSOL = false;
        cy.login(role, isBSOL);
        cy.getByTestId('search-patient-btn').click();
        // search patient
        cy.intercept('GET', '/SearchPatient*', {
            statusCode: 200,
            body: searchPatientPayload,
        }).as('search');
        cy.getByTestId('nhs-number-input').type(searchPatientPayload.nhsNumber);
        cy.getByTestId('search-submit-btn').click();
        cy.wait('@search');
    };

    gpRoles.forEach((role) => {
        beforeEach(() => {
            beforeEachConfiguration(role);
        });
        context(
            `View Lloyd George document for ${roleName(role)} role and download warning is present`,
            () => {
                it(
                    roleName(role) + ' can view a Lloyd George document of an active patient',
                    { tags: 'regression' },
                    () => {
                        cy.intercept('GET', '/LloydGeorgeStitch*', {
                            statusCode: 200,
                            body: viewLloydGeorgePayload,
                        }).as('lloydGeorgeStitch');

                        cy.get('#verify-submit').click();
                        cy.wait('@lloydGeorgeStitch');

                        // Assert
                        cy.getByTestId('before-downloading-warning').should(
                            'include.text',
                            'Before downloading',
                        );
                        assertPatientInfo();
                        cy.getByTestId('pdf-card')
                            .should('include.text', 'Lloyd George record')
                            .should('include.text', 'Last updated: 09 October 2023 at 15:41:38')
                            .should(
                                'include.text',
                                '12 files | File size: 502 KB | File format: PDF',
                            );
                        cy.getByTestId('pdf-viewer').should('be.visible');

                        // Act - open full screen view
                        cy.getByTestId('full-screen-btn').click();

                        // Assert
                        assertPatientInfo();
                        cy.getByTestId('pdf-card').should('not.exist');
                        cy.getByTestId('pdf-viewer').should('be.visible');

                        //  Act - close full screen view
                        cy.getByTestId('back-link').click();

                        // Assert
                        cy.getByTestId('pdf-card').should('be.visible');
                        cy.getByTestId('pdf-viewer').should('be.visible');
                    },
                );

                it(
                    `It displays an empty Lloyd George card when no Lloyd George record exists for the patient for a ${roleName(
                        role,
                    )}`,
                    { tags: 'regression' },
                    () => {
                        cy.intercept('GET', '/LloydGeorgeStitch*', {
                            statusCode: 404,
                        });
                        cy.get('#verify-submit').click();

                        // Assert
                        assertPatientInfo();
                        assertEmptyLloydGeorgeCard();
                    },
                );
                it(
                    `It displays an waiting message when uploading Lloyd George record is in progress for the patient for a ${roleName(
                        role,
                    )}`,
                    { tags: 'regression' },
                    () => {
                        cy.intercept('GET', '/LloydGeorgeStitch*', {
                            statusCode: 423,
                        });
                        cy.get('#verify-submit').click();

                        // Assert
                        assertPatientInfo();
                        cy.getByTestId('pdf-card').should('include.text', 'Lloyd George record');
                        cy.getByTestId('pdf-card').should(
                            'include.text',
                            'You can view this record once it’s finished uploading. This may take a few minutes.',
                        );
                    },
                );
                it(
                    `It displays an error when the Lloyd George Stitch API call fails for a ${roleName(
                        role,
                    )}`,
                    { tags: 'regression' },
                    () => {
                        cy.intercept('GET', '/LloydGeorgeStitch*', {
                            statusCode: 500,
                        });
                        cy.get('#verify-submit').click();

                        //Assert
                        cy.contains('Sorry, there is a problem with the service').should(
                            'be.visible',
                        );
                    },
                );

                it(
                    'Routes to download page when safety checkbox is checked',
                    { tags: 'regression' },
                    () => {
                        beforeEachConfiguration(role);
                        cy.intercept('GET', '/LloydGeorgeStitch*', {
                            statusCode: 200,
                            body: viewLloydGeorgePayload,
                        }).as('lloydGeorgeStitch');
                        cy.get('#verify-submit').click();
                        cy.wait('@lloydGeorgeStitch');

                        cy.getByTestId('download-and-remove-record-btn').click();
                        cy.getByTestId('confirm-download-and-remove-checkbox').should('exist');
                        cy.getByTestId('confirm-download-and-remove-checkbox').click();
                        cy.getByTestId('confirm-download-and-remove-btn').click();
                        cy.getByTestId('lloydgeorge_downloadall-stage').should('exist');
                    },
                );

                it(
                    'It displays warning when safety checkbox is not checked',
                    { tags: 'regression' },
                    () => {
                        beforeEachConfiguration(role);
                        cy.intercept('GET', '/LloydGeorgeStitch*', {
                            statusCode: 200,
                            body: viewLloydGeorgePayload,
                        }).as('lloydGeorgeStitch');
                        cy.get('#verify-submit').click();
                        cy.wait('@lloydGeorgeStitch');

                        cy.getByTestId('download-and-remove-record-btn').click();
                        cy.getByTestId('confirm-download-and-remove-checkbox').should('exist');
                        cy.getByTestId('confirm-download-and-remove-btn').click();
                        cy.getByTestId('confirm-download-and-remove-error').should('exist');
                    },
                );

                it(
                    'No download option or menu exists when no Lloyd George record exists for the patient',
                    { tags: 'regression' },
                    () => {
                        beforeEachConfiguration(role);

                        cy.intercept('GET', '/LloydGeorgeStitch*', {
                            statusCode: 404,
                        }).as('lloydGeorgeStitch');

                        cy.get('#verify-submit').click();
                        cy.wait('@lloydGeorgeStitch');

                        cy.getByTestId('download-all-files-link').should('not.exist');
                    },
                );

                it('Confirm download and delete of Lloyd George', { tags: 'regression' }, () => {
                    const isBSOL = false;
                    cy.login(role, isBSOL);
                    cy.getByTestId('search-patient-btn').click();

                    // search patient
                    cy.intercept('GET', '/SearchPatient*', {
                        statusCode: 200,
                        body: searchPatientPayload,
                    }).as('search');

                    cy.intercept('GET', '/LloydGeorgeStitch*', {
                        statusCode: 200,
                        body: viewLloydGeorgePayload,
                    }).as('lloydGeorgeStitch');

                    cy.intercept('POST', '/DocumentManifest*', (req) => {
                        req.reply({
                            statusCode: 200,
                            body: { jobId: 'test-jobId' },
                            delay: 500,
                        });
                    }).as('documentManifestPost');

                    cy.intercept('GET', '/DocumentManifest*', (req) => {
                        req.reply({
                            statusCode: 200,
                            body: { status: 'Completed', url: baseUrl + '/browserconfig.xml' }, // uses public served file in place of a ZIP file
                            delay: 500,
                        });
                    }).as('documentManifest');

                    cy.intercept('DELETE', '/DocumentDelete*', {
                        statusCode: 200,
                    }).as('documentDelete');

                    cy.getByTestId('nhs-number-input').type(searchPatientPayload.nhsNumber);
                    cy.getByTestId('search-submit-btn').click();
                    cy.wait('@search');

                    cy.get('#verify-submit').click();
                    cy.wait('@lloydGeorgeStitch');

                    cy.getByTestId('download-and-remove-record-btn').click();
                    cy.getByTestId('confirm-download-and-remove-checkbox').should('exist');
                    cy.getByTestId('confirm-download-and-remove-checkbox').click();
                    cy.getByTestId('confirm-download-and-remove-btn').click();
                    cy.getByTestId('lloydgeorge_downloadall-stage').should('exist');

                    // Assert contents of page when downloading
                    cy.contains('Downloading documents').should('be.visible');
                    cy.getByTestId(
                        'download-file-header-' + viewLloydGeorgePayload.number_of_files + '-files',
                    ).should('be.visible');
                    cy.contains('Compressing record into a zip file').should('be.visible');
                    cy.contains('Cancel').should('be.visible');

                    cy.wait('@documentManifest');
                    // Assert contents of page after download
                    cy.getByTestId('downloaded-record-card-header').should('be.visible');
                    cy.contains(
                        `${searchPatientPayload.givenName} ${searchPatientPayload.familyName}`,
                    ).should('be.visible');
                    cy.contains(
                        `NHS number: ${formatNhsNumber(searchPatientPayload.nhsNumber)}`,
                    ).should('be.visible');

                    // Assert file has been downloaded
                    cy.readFile(`${Cypress.config('downloadsFolder')}/browserconfig.xml`);
                    cy.wait('@documentDelete');
                    cy.getByTestId('return-btn').should('exist');
                    cy.contains('This record has been removed from our storage.').should(
                        'be.visible',
                    );
                    cy.contains('Follow the Record Management Code of Practice').should(
                        'be.visible',
                    );
                });
            },
        );
    });
});
