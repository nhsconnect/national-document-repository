import AWS from 'aws-sdk';

// need to get from env vars
AWS.config.update({
    accessKeyId: Cypress.env('AWS_ACCESS_KEY_ID'),
    secretAccessKey: Cypress.env('AWS_SECRET_ACCESS_KEY'),
    region: Cypress.env('AWS_REGION'),
    sessionToken: Cypress.env('AWS_SESSION_TOKEN'),
});

export default AWS;
