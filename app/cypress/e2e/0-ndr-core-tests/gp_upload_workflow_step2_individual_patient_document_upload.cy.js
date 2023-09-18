// env vars
const baseUrl = Cypress.env('CYPRESS_BASE_URL') ?? 'http://localhost:3000/';
const smokeTest = Cypress.env('CYPRESS_RUN_AS_SMOKETEST') ?? false;

const roles = Object.freeze({
    GP: 'gp',
    PCSE: 'pcse',
});
const formTypes = Object.freeze({
    LG: 'LG',
    ARF: 'ARF',
});
const testPatient = '9000000009';
const patient = {
    birthDate: '1970-01-01',
    familyName: 'Default Surname',
    givenName: ['Default Given Name'],
    nhsNumber: testPatient,
    postalCode: 'AA1 1AA',
    superseded: false,
    restricted: false,
};

const bucketUrlIdentifer = 'document-store.s3.amazonaws.com';
const serverError = 500;
const successNoContent = 204;

beforeEach(() => {
    cy.visit(baseUrl);
});

const selectForm = (formType) => cy.get(`#${formType}-documents-input`);

const navigateToUploadPage = () => {
    cy.intercept('GET', '/SearchPatient*', {
        statusCode: 200,
        body: patient,
    }).as('search');
    cy.get('#start-button').click();
    cy.get(`#${roles.GP}-radio-button`).click();
    cy.get('#role-submit-button').click();
    cy.get('#nhs-number-input').click();
    cy.get('#nhs-number-input').type(testPatient);

    cy.get('#search-submit').click();
    cy.wait('@search');
    cy.get('#verify-submit').click();
};

const clickUploadButton = () => {
    cy.get('#upload-button').click();
    cy.wait(20);
};

const testStartAgainButton = () => {
    cy.get('#start-again-button').should('have.text', 'Start Again');
    cy.get('#start-again-button').click();
    cy.url().should('eq', baseUrl);
};

const uploadedFilePathNames = [
    'cypress/fixtures/test_patient_record.pdf',
    'cypress/fixtures/test_patient_record_two.pdf',
];

const uploadedImagesPathNames = [
    'cypress/fixtures/test-images/test_image.jpg',
    'cypress/fixtures/test-images/test_image_two.jpg',
    'cypress/fixtures/test-images/test_image_three.jpg',
    'cypress/fixtures/test-images/test_image_four.jpg',
    'cypress/fixtures/test-images/test_image_five.jpg',
    'cypress/fixtures/test-images/test_image_six.jpg',
    'cypress/fixtures/test-images/test_image_seven.jpg',
    'cypress/fixtures/test-images/test_image_eight.jpg',
    'cypress/fixtures/test-images/test_image_nine.jpg',
    'cypress/fixtures/test-images/test_image_ten.jpg',
    'cypress/fixtures/test-images/test_image_eleven.jpg',
];

beforeEach(() => {
    cy.visit(baseUrl);
    navigateToUploadPage();
});
describe('[ALL] GP Upload Workflow Step 2: Uploads docs and tests it looks OK', () => {
    it('(Smoke test) On Start now button click, redirect to uploads is successful', () => {
        cy.url().should('include', 'upload');
        cy.url().should('eq', baseUrl + 'upload/submit');
    });

    it(`(Smoke test) Single file for both ARF and LG - On Upload button click, renders Upload Summary for successful upload`, () => {
        if (smokeTest === false) {
            cy.intercept('POST', '**/DocumentReference**', {
                statusCode: 200,
                body: {
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
            });

            cy.intercept('POST', '**' + bucketUrlIdentifer + '**', {
                statusCode: 204,
            });
        }

        selectForm(formTypes.ARF).selectFile(uploadedFilePathNames[0]);
        selectForm(formTypes.LG).selectFile(uploadedFilePathNames[1]);

        clickUploadButton();

        cy.get('#upload-summary-confirmation').should('be.visible');
        cy.get('#upload-summary-header').should('be.visible');
        cy.get('#successful-uploads-dropdown').should('be.visible');
        cy.get('#successful-uploads-dropdown').click();

        cy.get('#successful-uploads tbody tr').should('have.length', 2);
        cy.get('#successful-uploads tbody tr').eq(0).should('contain', 'test_patient_record.pdf');
        cy.get('#successful-uploads tbody tr')
            .eq(1)
            .should('contain', 'test_patient_record_two.pdf');
        cy.get('#close-page-warning').should('be.visible');

        testStartAgainButton();
    });
});

Object.values(formTypes).forEach((type) => {
    describe(`[${type}] GP Upload Workflow Step 2: Uploads docs and tests it looks OK`, () => {
        it(`(Smoke test) Single file - On Choose files button click, file selection is visible for ${type} input`, () => {
            cy.get('#selected-documents-table').should('not.exist');
            selectForm(type).selectFile(uploadedFilePathNames[0]);
            cy.get('#selected-documents-table').should('be.visible');
            cy.get('#selected-documents-table tbody tr').should('have.length', 1);
            cy.get('#selected-documents-table tbody tr')
                .first()
                .get('td')
                .first()
                .should('have.text', 'test_patient_record.pdf');
        });

        it(`Single file - On Upload button click, renders Upload Summary with error box when DocumentReference returns a 500 for ${type} input`, () => {
            // intercept this response and return an error
            cy.intercept('POST', '*/DocumentReference*', {
                statusCode: 500,
            });

            selectForm(type).selectFile(uploadedFilePathNames[0]);

            clickUploadButton();

            cy.get('#failed-document-uploads-summary-title').should('be.visible');
            cy.get('#failed-uploads').should('be.visible');
            cy.get('#failed-uploads tbody tr').should('have.length', 1);
            cy.get('#failed-uploads tbody tr')
                .first()
                .get('td')
                .first()
                .should('contain', 'test_patient_record.pdf');
            cy.get('#failed-uploads').should('contain', '1 of 1 files failed to upload');
            cy.get('#close-page-warning').should('be.visible');

            testStartAgainButton();
        });

        it(`Single file - On Upload button click, renders Upload Summary with error box when DocumentReference returns a 404 for ${type} input`, () => {
            // intercept this response and return an error
            cy.intercept('POST', '*/DocumentReference*', {
                statusCode: 404,
            });

            selectForm(type).selectFile(uploadedFilePathNames[1]);

            clickUploadButton();

            cy.get('#failed-document-uploads-summary-title').should('be.visible');
            cy.get('#failed-uploads').should('be.visible');
            cy.get('#failed-uploads tbody tr').should('have.length', 1);
            cy.get('#failed-uploads tbody tr')
                .first()
                .get('td')
                .first()
                .should('contain', 'test_patient_record_two.pdf');
            cy.get('#failed-uploads').should('contain', '1 of 1 files failed to upload');
            cy.get('#close-page-warning').should('be.visible');

            testStartAgainButton();
        });

        // once authorisation functionality has been added we can include a test like below for s3 bucket POST failure with 403 status

        it(`Single file - On Upload button click, renders Upload Summary with error box when the s3 bucket POST request fails for ${type} input`, () => {
            // intercept this response and return an error
            cy.intercept('POST', bucketUrlIdentifer, {
                statusCode: 500,
            });

            selectForm(type).selectFile(uploadedImagesPathNames[0]);

            clickUploadButton();

            cy.get('#failed-document-uploads-summary-title').should('be.visible');
            cy.get('#failed-uploads').should('be.visible');
            cy.get('#failed-uploads tbody tr').should('have.length', 1);
            cy.get('#failed-uploads tbody tr')
                .first()
                .get('td')
                .first()
                .should('contain', 'test_image.jpg');
            cy.get('#failed-uploads').should('contain', '1 of 1 files failed to upload');
            cy.get('#close-page-warning').should('be.visible');

            testStartAgainButton();
        });

        it(`(Smoke test) Multiple files - On Choose files button click, file selection is visible for ${type} input`, () => {
            cy.get('#selected-documents-table').should('not.exist');
            selectForm(type).selectFile(uploadedFilePathNames);
            cy.get('#selected-documents-table').should('be.visible');
            cy.get('#selected-documents-table tbody tr').should('have.length', 2);
            cy.get('#selected-documents-table tbody tr')
                .first()
                .get('td')
                .first()
                .should('have.text', 'test_patient_record.pdf');
            cy.get('#selected-documents-table tbody tr')
                .next()
                .contains('td', 'test_patient_record_two.pdf');
        });

        it(`(Smoke test) Multiple files - On Upload button click, renders Upload Summary for successful upload for ${type} input`, () => {
            if (smokeTest === false) {
                cy.intercept('POST', '**/DocumentReference**', {
                    statusCode: 200,
                    body: {
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
                });

                cy.intercept('POST', '**' + bucketUrlIdentifer + '**', {
                    statusCode: 204,
                });
            }

            selectForm(type).selectFile(uploadedFilePathNames);

            clickUploadButton();

            cy.get('#upload-summary-confirmation').should('be.visible');
            cy.get('#upload-summary-header').should('be.visible');
            cy.get('#successful-uploads-dropdown').should('be.visible');
            cy.get('#successful-uploads tbody tr').should('have.length', 2);
            cy.get('#successful-uploads tbody tr')
                .first()
                .get('td')
                .first()
                .should('contain', 'test_patient_record.pdf');
            cy.get('#close-page-warning').should('be.visible');

            testStartAgainButton();
        });

        it(`(Smoke test) Multiple files - On Upload button click, renders Uploading Stage for ${type} input`, () => {
            cy.intercept('POST', '**/DocumentReference*', (req) => {
                req.reply({
                    statusCode: 200,
                    body: {
                        url: bucketUrlIdentifer,
                        fields: {
                            key: '382d3db4-9625-4bd9-ad46-c2e31451efd2',
                            'x-amz-algorithm': 'AWS4-HMAC-SHA256',
                            'x-amz-credential':
                                'ASIAXYSUA44VYD2FFBHK/20230904/eu-west-2/s3/aws4_request',
                            'x-amz-date': '20230904T125954Z',
                            'x-amz-security-token':
                                'IQoJb3JpZ2luX2VjEG0aCWV1LXdlc3QtMiJHMEUCIQC1Mx4VTrF2alA9s8P5HJ+j9y2XJmAF5ODdZGEui/QMGwIgRdGiuXVqq8Uq6l5dJZpAx39b1kro7x1Q0FQn6rWRUvUqggMIRhABGgw1MzM4MjU5MDY0NzUiDOeBIQxpj1BmAtTeVSrfAsugZpo7cQzj+R0uwE9o3bxMyR7lqdVCkaAb/ZVF4iBY/Cn7FYCB+pO3nvS6CWLClcIbNhhZkqgJOZvBJ+fua5QvchxX4LO+sq0Or+s29Ym8mSNHpB4mLi3iyQZ08Iw1p9c52Mfo6B5mh5IGKu8gvKf1y9gOWKAJTTuLbuzKKkbII4tRr+1PSAeFwLgSSzeDInv9QnTbKAPSbVMAWBic07MTlQpeMD3SNiXqKz+f/HNiujCOxfvUO0Yvw5GXx0FBrGjaHY979YGJuuC35yMqnFG0tvdd/8OfdUhHDM6XqRMGmceMkdMldQsw4VwhSd+uI4qIrHopMNQ+XKdqDjrkmlRprATIT9boO1fQ1GFO2l1YVVM2WzORIwVd2hGQr6anfXyOePk8N8MYNuzwZdgOiEKPwS2b6vByMBr/U7jNUuUZNd9rhbZIv5dsMF2xszXq8co3ZngvPjWKYsdZF6eGUDDHqdenBjqeAYZZ0oBZqtgVF3ebT86UWZ40zS0vGZSzSt5P5DhlTP01LRPeQCARoETZ/IsUzvrP5QLwmkOjSoJlYIu/U1SeqvVZblnPHsHVi/0QI4FuZhPL9LnA628+euBTaO6I2DSf1ugPmwMc/YMYwHQdkSKNsejAPczYSxAyPAWLtiLckMPqo5YyyiRYMHpmZwrqJsdbAVogVhIgfYx53OJIhblI',
                            policy: 'eyJleHBpcmF0aW9uIjogIjIwMjMtMDktMDRUMTM6Mjk6NTRaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAibmRyYS1kb2N1bWVudC1zdG9yZSJ9LCB7ImtleSI6ICIzODJkM2RiNC05NjI1LTRiZDktYWQ0Ni1jMmUzMTQ1MWVmZDIifSwgeyJ4LWFtei1hbGdvcml0aG0iOiAiQVdTNC1ITUFDLVNIQTI1NiJ9LCB7IngtYW16LWNyZWRlbnRpYWwiOiAiQVNJQVhZU1VBNDRWWUQyRkZCSEsvMjAyMzA5MDQvZXUtd2VzdC0yL3MzL2F3czRfcmVxdWVzdCJ9LCB7IngtYW16LWRhdGUiOiAiMjAyMzA5MDRUMTI1OTU0WiJ9LCB7IngtYW16LXNlY3VyaXR5LXRva2VuIjogIklRb0piM0pwWjJsdVgyVmpFRzBhQ1dWMUxYZGxjM1F0TWlKSE1FVUNJUUMxTXg0VlRyRjJhbEE5czhQNUhKK2o5eTJYSm1BRjVPRGRaR0V1aS9RTUd3SWdSZEdpdVhWcXE4VXE2bDVkSlpwQXgzOWIxa3JvN3gxUTBGUW42cldSVXZVcWdnTUlSaEFCR2d3MU16TTRNalU1TURZME56VWlET2VCSVF4cGoxQm1BdFRlVlNyZkFzdWdacG83Y1F6aitSMHV3RTlvM2J4TXlSN2xxZFZDa2FBYi9aVkY0aUJZL0NuN0ZZQ0IrcE8zbnZTNkNXTENsY0liTmhoWmtxZ0pPWnZCSitmdWE1UXZjaHhYNExPK3NxME9yK3MyOVltOG1TTkhwQjRtTGkzaXlRWjA4SXcxcDljNTJNZm82QjVtaDVJR0t1OGd2S2YxeTlnT1dLQUpUVHVMYnV6S0trYklJNHRScisxUFNBZUZ3TGdTU3plREludjlRblRiS0FQU2JWTUFXQmljMDdNVGxRcGVNRDNTTmlYcUt6K2YvSE5pdWpDT3hmdlVPMFl2dzVHWHgwRkJyR2phSFk5NzlZR0p1dUMzNXlNcW5GRzB0dmRkLzhPZmRVaEhETTZYcVJNR21jZU1rZE1sZFFzdzRWd2hTZCt1STRxSXJIb3BNTlErWEtkcURqcmttbFJwckFUSVQ5Ym9PMWZRMUdGTzJsMVlWVk0yV3pPUkl3VmQyaEdRcjZhbmZYeU9lUGs4TjhNWU51endaZGdPaUVLUHdTMmI2dkJ5TUJyL1U3ak5VdVVaTmQ5cmhiWkl2NWRzTUYyeHN6WHE4Y28zWm5ndlBqV0tZc2RaRjZlR1VEREhxZGVuQmpxZUFZWlowb0JacXRnVkYzZWJUODZVV1o0MHpTMHZHWlN6U3Q1UDVEaGxUUDAxTFJQZVFDQVJvRVRaL0lzVXp2clA1UUx3bWtPalNvSmxZSXUvVTFTZXF2VlpibG5QSHNIVmkvMFFJNEZ1WmhQTDlMbkE2MjgrZXVCVGFPNkkyRFNmMXVnUG13TWMvWU1Zd0hRZGtTS05zZWpBUGN6WVN4QXlQQVdMdGlMY2tNUHFvNVl5eWlSWU1IcG1ad3JxSnNkYkFWb2dWaElnZll4NTNPSkloYmxJIn1dfQ==',
                            'x-amz-signature':
                                '9e861ee405f4930c8fd992e631fa202563b50b23c2f505cbfcbd407198cd594d',
                        },
                    },
                });
                req.on('response', (res) => {
                    // Throttle the response to 1 Mbps to simulate a
                    // mobile 3G connection
                    res.setThrottle(1000);
                });
            });

            selectForm(type).selectFile(uploadedImagesPathNames);

            clickUploadButton();

            cy.get('#upload-stage-warning').should('be.visible');
        });

        it(`Multiple files - On Upload button click, renders Upload Summary with error box when DocumentReference returns a 500 for ${type} input`, () => {
            // intercept this response and return an error
            cy.intercept('POST', '*/DocumentReference*', {
                statusCode: 500,
            });

            selectForm(type).selectFile(uploadedImagesPathNames);

            clickUploadButton();

            cy.get('#failed-document-uploads-summary-title').should('be.visible');
            cy.get('#failed-uploads').should('be.visible');
            cy.get('#failed-uploads tbody tr').should('have.length', 11);
            cy.get('#failed-uploads tbody tr')
                .first()
                .get('td')
                .first()
                .should('contain', 'test_image.jpg');
            cy.get('#failed-uploads').should('contain', '11 of 11 files failed to upload');
            cy.get('#close-page-warning').should('be.visible');

            testStartAgainButton();
        });

        it(`Multiple files - On Upload button click, renders Upload Summary with error box when DocumentReference returns a 404 for ${type} input`, () => {
            // intercept this response and return an error
            cy.intercept('POST', '*/DocumentReference*', {
                statusCode: 404,
            });

            selectForm(type).selectFile(uploadedImagesPathNames);

            clickUploadButton();

            cy.get('#failed-document-uploads-summary-title').should('be.visible');
            cy.get('#failed-uploads').should('be.visible');
            cy.get('#failed-uploads tbody tr').should('have.length', 11);
            cy.get('#failed-uploads tbody tr')
                .first()
                .get('td')
                .first()
                .should('contain', 'test_image.jpg');
            cy.get('#failed-uploads').should('contain', '11 of 11 files failed to upload');
            cy.get('#close-page-warning').should('be.visible');

            testStartAgainButton();
        });

        it(`Multiple files - On Upload button click, renders Upload Summary with both failed and successful documents for ${type} input`, () => {
            cy.intercept('POST', '**/DocumentReference*', {
                statusCode: 200,
                body: {
                    url: bucketUrlIdentifer,
                    fields: {
                        key: '382d3db4-9625-4bd9-ad46-c2e31451efd2',
                        'x-amz-algorithm': 'AWS4-HMAC-SHA256',
                        'x-amz-credential':
                            'ASIAXYSUA44VYD2FFBHK/20230904/eu-west-2/s3/aws4_request',
                        'x-amz-date': '20230904T125954Z',
                        'x-amz-security-token':
                            'IQoJb3JpZ2luX2VjEG0aCWV1LXdlc3QtMiJHMEUCIQC1Mx4VTrF2alA9s8P5HJ+j9y2XJmAF5ODdZGEui/QMGwIgRdGiuXVqq8Uq6l5dJZpAx39b1kro7x1Q0FQn6rWRUvUqggMIRhABGgw1MzM4MjU5MDY0NzUiDOeBIQxpj1BmAtTeVSrfAsugZpo7cQzj+R0uwE9o3bxMyR7lqdVCkaAb/ZVF4iBY/Cn7FYCB+pO3nvS6CWLClcIbNhhZkqgJOZvBJ+fua5QvchxX4LO+sq0Or+s29Ym8mSNHpB4mLi3iyQZ08Iw1p9c52Mfo6B5mh5IGKu8gvKf1y9gOWKAJTTuLbuzKKkbII4tRr+1PSAeFwLgSSzeDInv9QnTbKAPSbVMAWBic07MTlQpeMD3SNiXqKz+f/HNiujCOxfvUO0Yvw5GXx0FBrGjaHY979YGJuuC35yMqnFG0tvdd/8OfdUhHDM6XqRMGmceMkdMldQsw4VwhSd+uI4qIrHopMNQ+XKdqDjrkmlRprATIT9boO1fQ1GFO2l1YVVM2WzORIwVd2hGQr6anfXyOePk8N8MYNuzwZdgOiEKPwS2b6vByMBr/U7jNUuUZNd9rhbZIv5dsMF2xszXq8co3ZngvPjWKYsdZF6eGUDDHqdenBjqeAYZZ0oBZqtgVF3ebT86UWZ40zS0vGZSzSt5P5DhlTP01LRPeQCARoETZ/IsUzvrP5QLwmkOjSoJlYIu/U1SeqvVZblnPHsHVi/0QI4FuZhPL9LnA628+euBTaO6I2DSf1ugPmwMc/YMYwHQdkSKNsejAPczYSxAyPAWLtiLckMPqo5YyyiRYMHpmZwrqJsdbAVogVhIgfYx53OJIhblI',
                        policy: 'eyJleHBpcmF0aW9uIjogIjIwMjMtMDktMDRUMTM6Mjk6NTRaIiwgImNvbmRpdGlvbnMiOiBbeyJidWNrZXQiOiAibmRyYS1kb2N1bWVudC1zdG9yZSJ9LCB7ImtleSI6ICIzODJkM2RiNC05NjI1LTRiZDktYWQ0Ni1jMmUzMTQ1MWVmZDIifSwgeyJ4LWFtei1hbGdvcml0aG0iOiAiQVdTNC1ITUFDLVNIQTI1NiJ9LCB7IngtYW16LWNyZWRlbnRpYWwiOiAiQVNJQVhZU1VBNDRWWUQyRkZCSEsvMjAyMzA5MDQvZXUtd2VzdC0yL3MzL2F3czRfcmVxdWVzdCJ9LCB7IngtYW16LWRhdGUiOiAiMjAyMzA5MDRUMTI1OTU0WiJ9LCB7IngtYW16LXNlY3VyaXR5LXRva2VuIjogIklRb0piM0pwWjJsdVgyVmpFRzBhQ1dWMUxYZGxjM1F0TWlKSE1FVUNJUUMxTXg0VlRyRjJhbEE5czhQNUhKK2o5eTJYSm1BRjVPRGRaR0V1aS9RTUd3SWdSZEdpdVhWcXE4VXE2bDVkSlpwQXgzOWIxa3JvN3gxUTBGUW42cldSVXZVcWdnTUlSaEFCR2d3MU16TTRNalU1TURZME56VWlET2VCSVF4cGoxQm1BdFRlVlNyZkFzdWdacG83Y1F6aitSMHV3RTlvM2J4TXlSN2xxZFZDa2FBYi9aVkY0aUJZL0NuN0ZZQ0IrcE8zbnZTNkNXTENsY0liTmhoWmtxZ0pPWnZCSitmdWE1UXZjaHhYNExPK3NxME9yK3MyOVltOG1TTkhwQjRtTGkzaXlRWjA4SXcxcDljNTJNZm82QjVtaDVJR0t1OGd2S2YxeTlnT1dLQUpUVHVMYnV6S0trYklJNHRScisxUFNBZUZ3TGdTU3plREludjlRblRiS0FQU2JWTUFXQmljMDdNVGxRcGVNRDNTTmlYcUt6K2YvSE5pdWpDT3hmdlVPMFl2dzVHWHgwRkJyR2phSFk5NzlZR0p1dUMzNXlNcW5GRzB0dmRkLzhPZmRVaEhETTZYcVJNR21jZU1rZE1sZFFzdzRWd2hTZCt1STRxSXJIb3BNTlErWEtkcURqcmttbFJwckFUSVQ5Ym9PMWZRMUdGTzJsMVlWVk0yV3pPUkl3VmQyaEdRcjZhbmZYeU9lUGs4TjhNWU51endaZGdPaUVLUHdTMmI2dkJ5TUJyL1U3ak5VdVVaTmQ5cmhiWkl2NWRzTUYyeHN6WHE4Y28zWm5ndlBqV0tZc2RaRjZlR1VEREhxZGVuQmpxZUFZWlowb0JacXRnVkYzZWJUODZVV1o0MHpTMHZHWlN6U3Q1UDVEaGxUUDAxTFJQZVFDQVJvRVRaL0lzVXp2clA1UUx3bWtPalNvSmxZSXUvVTFTZXF2VlpibG5QSHNIVmkvMFFJNEZ1WmhQTDlMbkE2MjgrZXVCVGFPNkkyRFNmMXVnUG13TWMvWU1Zd0hRZGtTS05zZWpBUGN6WVN4QXlQQVdMdGlMY2tNUHFvNVl5eWlSWU1IcG1ad3JxSnNkYkFWb2dWaElnZll4NTNPSkloYmxJIn1dfQ==',
                        'x-amz-signature':
                            '9e861ee405f4930c8fd992e631fa202563b50b23c2f505cbfcbd407198cd594d',
                    },
                },
            });

            let requestCount = 0;
            cy.intercept('POST', '**' + bucketUrlIdentifer + '**', (req) => {
                requestCount += 1;
                req.reply({
                    statusCode: requestCount % 2 === 1 ? serverError : successNoContent,
                });
            });

            selectForm(type).selectFile(uploadedImagesPathNames);

            clickUploadButton();

            cy.get('#upload-summary-header').should('be.visible');
            cy.get('#failed-uploads').should('contain', '6 of 11 files failed to upload');
            cy.get('#failed-uploads tbody tr').should('have.length', 6);
            cy.get('#successful-uploads tbody tr').should('have.length', 5);
            cy.get('#close-page-warning').should('be.visible');

            testStartAgainButton();
        });
    });
});
