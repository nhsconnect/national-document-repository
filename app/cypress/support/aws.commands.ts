/// <reference types="cypress" />

import AWS from './aws.config';

Cypress.Commands.add('addFileToS3', (bucketName: string, fileName: string, filePath: string) => {
    const s3 = new AWS.S3();

    return cy.fixture(filePath, 'binary').then((fileContent) => {
        const params: AWS.S3.Types.PutObjectRequest = {
            Bucket: bucketName,
            Key: fileName,
            Body: fileContent,
        };

        return cy.wrap(
            new Cypress.Promise((resolve, reject) => {
                s3.upload(params, (err, data) => {
                    if (err) {
                        const message = 'Error uploading file to S3:' + err;
                        console.error(message);
                        reject(message);
                    } else {
                        console.log('File uploaded successfully to S3:', data.Location);
                        resolve(data);
                    }
                });
            }),
        );
    });
});

Cypress.Commands.add(
    'addItemToDynamoDb',
    (tableName: string, item: AWS.DynamoDB.PutItemInputAttributeMap) => {
        const dynamoDB = new AWS.DynamoDB();

        const params: AWS.DynamoDB.PutItemInput = {
            TableName: tableName,
            Item: AWS.DynamoDB.Converter.marshall(item),
        };

        return cy.wrap(
            new Cypress.Promise((resolve, reject) => {
                dynamoDB.putItem(params, (err, data) => {
                    if (err) {
                        const message = 'Error uploading to Dynamo:' + tableName;
                        console.error(message);
                        reject(message);
                    } else {
                        console.log('Upload to Dynamo success:', tableName);
                        resolve(data);
                    }
                });
            }),
        );
    },
);

Cypress.Commands.add('deleteFileFromS3', (bucketName: string, fileName: string) => {
    const s3 = new AWS.S3();

    const params: AWS.S3.Types.DeleteObjectRequest = {
        Bucket: bucketName,
        Key: fileName,
    };

    return cy.wrap(
        new Cypress.Promise((resolve, reject) => {
            s3.deleteObject(params, (err, data) => {
                if (err) {
                    const message = 'Error uploading to S3:' + bucketName;
                    console.error(message);
                    reject(message);
                } else {
                    console.log('Upload to S3 success:', bucketName);
                    resolve(data);
                }
            });
        }),
    );
});

Cypress.Commands.add('deleteItemFromDynamoDb', (tableName: string, itemId: string) => {
    const dynamoDB = new AWS.DynamoDB();

    const params: AWS.DynamoDB.Types.DeleteItemInput = {
        TableName: tableName,
        Key: {
            ID: { S: itemId },
        },
    };

    return cy.wrap(
        new Cypress.Promise((resolve, reject) => {
            dynamoDB.deleteItem(params, (err, data) => {
                if (err) {
                    const message = 'Error uploading to Dynamo:' + tableName;
                    console.error(message);
                    reject(message);
                } else {
                    console.log('Upload to Dynamo success:', tableName);
                    resolve(data);
                }
            });
        }),
    );
});
