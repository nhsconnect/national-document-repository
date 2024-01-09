import AWS from 'aws-sdk';

// need to get from env vars
AWS.config.update({
    accessKeyId: Cypress.env('AWS_accessKeyId'),
    secretAccessKey: Cypress.env('AWS_secretAccessKey'),
    region: Cypress.env('AWS_region'),
    sessionToken: Cypress.env('AWS_sessionToken'),
});

export default AWS;
