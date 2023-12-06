/// <reference types="cypress" />

import AWS from './aws.config';

Cypress.Commands.add('uploadFileToS3', () => {
    const s3 = new AWS.S3();

    // set as params / env vars
    const bucketName = '';
    const fileName = '';
    const fileContent = '';

    const params: AWS.S3.Types.PutObjectRequest = {
        Bucket: bucketName,
        Key: fileName,
        Body: fileContent,
    };

    s3.upload(params, (err, data) => {
        if (err) {
            console.error('Error uploading file to S3:', err);
        } else {
            console.log('File uploaded successfully to S3:', data.Location);
        }
    });
});

Cypress.Commands.add('addDynamoDBEntry', (item) => {
    const dynamoDB = new AWS.DynamoDB();

    // set as method params / env vars / alt commands for each db table?
    const params = {
        TableName: 'MyTable',
        Item: AWS.DynamoDB.Converter.marshall(JSON.parse(item)),
    };

    return cy.wrap(dynamoDB.putItem(params).promise(), { timeout: 10000 });
});
