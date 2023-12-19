/// <reference types="cypress" />

import AWS from './aws.config';

Cypress.Commands.add('addFileToS3', (bucketName, fileName, fileContent) => {
    const s3 = new AWS.S3();

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

Cypress.Commands.add('addItemToDynamoDb', (tableName, item) => {
    const dynamoDB = new AWS.DynamoDB();

    const params = {
        TableName: tableName,
        Item: AWS.DynamoDB.Converter.marshall(item),
    };

    return cy.wrap(dynamoDB.putItem(params).promise(), { timeout: 10000 });
});

Cypress.Commands.add('deleteFileFromS3', (bucketName: string, fileName: string) => {
    const s3 = new AWS.S3();

    const params: AWS.S3.Types.DeleteObjectRequest = {
        Bucket: bucketName,
        Key: fileName,
    };

    return cy.wrap(s3.deleteObject(params).promise(), { timeout: 10000 }).then(() => {
        console.log('File deleted successfully from S3:', fileName);
    });
});

Cypress.Commands.add('deleteItemFromDynamoDb', (tableName: string, itemId: string) => {
    const dynamoDB = new AWS.DynamoDB();

    const params: AWS.DynamoDB.Types.DeleteItemInput = {
        TableName: tableName,
        Key: {
            ID: { S: itemId },
        },
    };

    return cy.wrap(dynamoDB.deleteItem(params).promise(), { timeout: 10000 }).then(() => {
        console.log('Item deleted successfully from DynamoDB:', itemId);
    });
});
