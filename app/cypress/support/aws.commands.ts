/// <reference types="cypress" />

import AWS from './aws.config';
import { QueryOutput } from 'aws-sdk/clients/dynamodb';

Cypress.Commands.add('addPdfFileToS3', (bucketName: string, fileName: string, filePath: string) => {
    const s3 = new AWS.S3();

    return cy.fixture(filePath, null).then((fileContent) => {
        const params: AWS.S3.Types.PutObjectRequest = {
            Bucket: bucketName,
            Key: fileName,
            Body: fileContent,
            ContentType: 'application/pdf',
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

function isEmpty(value: unknown) {
    return value == null || (typeof value === 'string' && value.trim().length === 0);
}

Cypress.Commands.add(
    'deleteItemsBySecondaryKeyFromDynamoDb',
    (tableName: string, index: string, attribute: string, value: string) => {
        const dynamoDB = new AWS.DynamoDB();

        const queryParams: AWS.DynamoDB.Types.QueryInput = {
            TableName: tableName,
            IndexName: index,
            KeyConditionExpression: `${attribute} = :v1`,
            ExpressionAttributeValues: {
                ':v1': {
                    S: value,
                },
            },
            ProjectionExpression: 'ID',
        };

        //queries table with the index and specific value
        return cy.wrap(
            new Cypress.Promise((resolve, reject) => {
                dynamoDB.query(queryParams, (err, data) => {
                    if (err) {
                        console.error(`Error querying Dynamo: ${tableName}`);
                        reject('Error querying Dynamo:' + tableName);
                    } else {
                        console.log(`'Dynamo query success: ${tableName}`);
                        resolve(data);
                    }
                });
            }).then((value) => {
                //uses the returned query response to form a batch write request and delete each item
                const itemsForDelete = (value as QueryOutput).Items;

                if (
                    itemsForDelete?.length === 0 ||
                    itemsForDelete === undefined ||
                    itemsForDelete === null
                ) {
                    Cypress.log({
                        name: 'deleteItemBySecondaryKeyFromDynamoDb',
                        displayName: 'WARNING: Delete items',
                        message: `itemsForDelete was empty, undefined or null`,
                    });

                    return;
                }

                const itemIDs: Array<string> = [];

                itemsForDelete?.forEach((element) => {
                    if (isEmpty(element.ID.S) || element.ID.S === undefined) {
                        throw new Error(` ID is empty, blank, undefined or null for ${element}`);
                    }

                    itemIDs.push(element.ID.S);
                });

                const batchDeleteParams = {
                    RequestItems: {
                        [tableName]: itemIDs.map((item) => ({
                            DeleteRequest: {
                                Key: {
                                    ID: { S: item },
                                },
                            },
                        })),
                    },
                };

                dynamoDB.batchWriteItem(batchDeleteParams, (err, data) => {
                    if (err) {
                        console.error(`Error during batch delete: ${tableName}`, err);
                        throw err;
                    } else {
                        console.log('Dynamo batch delete success:', tableName, data);
                        return data;
                    }
                });
            }),
        );
    },
);
