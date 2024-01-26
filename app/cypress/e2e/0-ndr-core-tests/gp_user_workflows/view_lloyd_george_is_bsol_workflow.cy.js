import viewLloydGeorgePayload from '../../../fixtures/requests/GET_LloydGeorgeStitch.json';
import searchPatientPayload from '../../../fixtures/requests/GET_SearchPatient.json';
import { Roles, roleName } from '../../../support/roles';

const baseUrl = Cypress.config('baseUrl');
const gpRoles = [Roles.GP_ADMIN, Roles.GP_CLINICAL];

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
        cy.getByTestId('llyoyd-george-record-error-message').should(
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
        cy.login(role);
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
        context(`View Lloyd George document for ${roleName(role)} role`, () => {
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
                    assertPatientInfo();
                    cy.getByTestId('pdf-card')
                        .should('include.text', 'Lloyd George record')
                        .should('include.text', 'Last updated: 09 October 2023 at 15:41:38')
                        .should('include.text', '12 files | File size: 502 KB | File format: PDF');
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
                    cy.contains('Sorry, there is a problem with the service').should('be.visible');
                },
            );
        });
    });

    context('View Lloyd George document with specific role tests', () => {
        it(
            'It displays an error with a download link when a Lloyd George stitching timeout occurs via the API Gateway for a GP_ADMIN',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);
                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 504,
                });
                cy.get('#verify-submit').click();

                //Assert
                assertTimeoutLloydGeorgeError(true);
            },
        );

        it(
            'It displays an error with download link when a Lloyd George stitching timeout occurs via the API Gateway for a GP_CLINICAL but link access is denied',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_CLINICAL);
                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 504,
                });
                cy.get('#verify-submit').click();

                //Assert
                assertTimeoutLloydGeorgeError(false);
            },
        );
    });

    context('Delete Lloyd George document', () => {
        it(
            'A GP ADMIN user can delete the Lloyd George document of an active patient',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);

                let request = 0;
                const replies = [
                    { statusCode: 200, body: viewLloydGeorgePayload },
                    { statusCode: 404 },
                ];

                cy.intercept('GET', '/LloydGeorgeStitch*', (req) => {
                    req.reply(replies[request]);
                    request = request + 1;
                }).as('lloydGeorgeStitch');

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');

                cy.getByTestId('actions-menu').click();
                cy.getByTestId('delete-all-files-link').click();

                // assert delete confirmation page is as expected
                cy.contains('Are you sure you want to permanently delete files for:').should(
                    'be.visible',
                );
                cy.contains('GivenName Surname').should('be.visible');
                cy.contains('NHS number: 900 000 0009').should('be.visible');
                cy.contains('Date of birth: 01 January 1970').should('be.visible');

                cy.intercept(
                    'DELETE',
                    `/DocumentDelete?patientId=${searchPatientPayload.nhsNumber}&docType=LG`,
                    {
                        statusCode: 200,
                        body: 'Success',
                    },
                ).as('documentDelete');

                cy.getByTestId('yes-radio-btn').click();
                cy.getByTestId('delete-submit-btn').click();

                cy.wait('@documentDelete');

                // assert delete success page is as expected
                cy.contains('Deletion complete').should('be.visible');
                cy.contains('12 files from the Lloyd George record of:').should('be.visible');
                cy.contains('GivenName Surname').should('be.visible');
                cy.contains('(NHS number: 900 000 0009)').should('be.visible');

                cy.getByTestId('lg-return-btn').click();

                // assert user is returned to view Lloyd George page
                cy.contains('Lloyd George record').should('be.visible');
                cy.contains('No documents are available').should('be.visible');
                cy.getByTestId('pdf-card').should('be.visible');
            },
        );

        it(
            'Page returns user to view Lloyd George page on the cancel action of delete as a GP ADMIN',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);

                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 200,
                    body: viewLloydGeorgePayload,
                }).as('lloydGeorgeStitch');

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');

                cy.getByTestId('actions-menu').click();
                cy.getByTestId('delete-all-files-link').click();

                // cancel delete
                cy.getByTestId('no-radio-btn').click();
                cy.getByTestId('delete-submit-btn').click();

                // assert user is returned to view Lloyd George page
                cy.contains('Lloyd George record').should('be.visible');
                cy.getByTestId('pdf-card').should('be.visible');
                cy.getByTestId('pdf-viewer').should('be.visible');
            },
        );

        it(
            'It displays an error when the delete Lloyd George document API call fails as A GP ADMIN',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_ADMIN);

                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 200,
                    body: viewLloydGeorgePayload,
                }).as('lloydGeorgeStitch');

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');

                cy.getByTestId('actions-menu').click();
                cy.getByTestId('delete-all-files-link').click();

                cy.intercept(
                    'DELETE',
                    `/DocumentDelete?patientId=${searchPatientPayload.nhsNumber}&docType=LG`,
                    {
                        statusCode: 500,
                        body: 'Failed to delete documents',
                    },
                ).as('documentDelete');

                cy.getByTestId('yes-radio-btn').click();
                cy.getByTestId('delete-submit-btn').click();

                cy.wait('@documentDelete');

                // assert
                cy.contains('Sorry, there is a problem with the service').should('be.visible');
            },
        );

        it(
            'No download option or menu exists when no Lloyd George record exists for the patient for a GP CLINICAL user',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_CLINICAL);

                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 404,
                }).as('lloydGeorgeStitch');

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');

                cy.getByTestId('actions-menu').should('not.exist');
            },
        );

        it(
            'No download option exists when a Lloyd George record exists for a GP CLINICAL user',
            { tags: 'regression' },
            () => {
                beforeEachConfiguration(Roles.GP_CLINICAL);
                cy.intercept('GET', '/LloydGeorgeStitch*', {
                    statusCode: 200,
                    body: viewLloydGeorgePayload,
                }).as('lloydGeorgeStitch');

                cy.get('#verify-submit').click();
                cy.wait('@lloydGeorgeStitch');

                cy.getByTestId('actions-menu').should('not.exist');
            },
        );
    });

    context('Delete Lloyd George document', () => {
        it('displays an error when the document manifest backend API call fails as a PCSE user', () => {
            beforeEachConfiguration(Roles.PCSE);
            cy.intercept('GET', '/SearchDocumentReferences*', {
                statusCode: 200,
                body: [
                    { fileName: 'testName', created: 'testCreated', virusScannerResult: 'Clean' },
                ],
            }).as('searchDocs');

            cy.intercept('GET', '/DocumentManifest*', {
                statusCode: 500,
            }).as('documentManifest');

            cy.get('#verify-submit').click();
            cy.wait('@searchDocs');
            cy.get('#download-documents').click();
            cy.wait('@documentManifest');

            // Assert
            cy.contains('Sorry, there is a problem with the service').should('be.visible');
        });
    });
});
