/// <reference types="cypress" />

import aws from './aws.config';
import './commands';
import {
    S3Client,
    PutObjectCommand,
    DeleteObjectCommand,
    PutObjectCommandInput,
    DeleteObjectCommandInput,
} from '@aws-sdk/client-s3';

import {
    DynamoDBClient,
    PutItemCommand,
    DeleteItemCommand,
    QueryCommand,
    BatchWriteItemCommand,
    PutItemCommandInput,
    DeleteItemCommandInput,
    QueryCommandInput,
    QueryCommandOutput,
    BatchWriteItemCommandInput,
} from '@aws-sdk/client-dynamodb';

import { marshall } from '@aws-sdk/util-dynamodb';

const s3: S3Client = aws.s3;
const dynamo: DynamoDBClient = aws.dynamo;

Cypress.Commands.add('addPdfFileToS3', (bucketName: string, fileName: string, filePath: string) => {
    return cy.fixture(filePath, null).then((fileContent) => {
        const body = Cypress.Buffer.from(new Uint8Array(fileContent as ArrayBuffer));

        const params: PutObjectCommandInput = {
            Bucket: bucketName,
            Key: fileName,
            Body: body,
            ContentType: 'application/pdf',
        };

        return cy.wrap(
            s3
                .send(new PutObjectCommand(params))
                .then((data) => {
                    return data;
                })
                .catch((err) => {
                    const message = 'Error uploading file to S3: ' + err;
                    // eslint-disable-next-line no-console
                    console.error(message);
                    throw new Error(message);
                }),
        );
    });
});

Cypress.Commands.add('addItemToDynamoDb', (tableName: string, item: Record<string, unknown>) => {
    const params: PutItemCommandInput = {
        TableName: tableName,
        Item: marshall(item),
    };

    return cy.wrap(
        dynamo
            .send(new PutItemCommand(params))
            .then((data) => data)
            .catch((err) => {
                const message = 'Error uploading to Dynamo: ' + tableName;
                // eslint-disable-next-line no-console
                console.error(message, err);
                throw new Error(message);
            }),
    );
});

Cypress.Commands.add('deleteFileFromS3', (bucketName: string, fileName: string) => {
    const params: DeleteObjectCommandInput = {
        Bucket: bucketName,
        Key: fileName,
    };

    return cy.wrap(
        s3
            .send(new DeleteObjectCommand(params))
            .then((data) => data)
            .catch((err) => {
                const message = 'Error deleting object from S3: ' + bucketName;
                // eslint-disable-next-line no-console
                console.error(message, err);
                throw new Error(message);
            }),
    );
});

Cypress.Commands.add('deleteItemFromDynamoDb', (tableName: string, itemId: string) => {
    const params: DeleteItemCommandInput = {
        TableName: tableName,
        Key: {
            ID: { S: itemId },
        },
    };

    return cy.wrap(
        dynamo
            .send(new DeleteItemCommand(params))
            .then((data) => data)
            .catch((err) => {
                const message = 'Error deleting item from Dynamo: ' + tableName;
                // eslint-disable-next-line no-console
                console.error(message, err);
                throw new Error(message);
            }),
    );
});

Cypress.Commands.add(
    'deleteItemsBySecondaryKeyFromDynamoDb',
    (
        tableName: string,
        index: string,
        attribute: string,
        value: string,
    ): Cypress.Chainable<void> => {
        const queryParams: QueryCommandInput = {
            TableName: tableName,
            IndexName: index,
            KeyConditionExpression: `${attribute} = :v1`,
            ExpressionAttributeValues: { ':v1': { S: value } },
            ProjectionExpression: 'ID',
        };

        return cy.then(async (): Promise<void> => {
            const data = (await dynamo.send(new QueryCommand(queryParams))) as QueryCommandOutput;

            const items = data.Items ?? [];
            if (items.length === 0) {
                Cypress.log({
                    name: 'deleteItemsBySecondaryKeyFromDynamoDb',
                    displayName: 'WARNING: Delete items',
                    message: 'itemsForDelete was empty, undefined or null',
                });
                return;
            }

            const itemIDs = items.map((el) => {
                const id = el?.ID?.S?.trim();
                if (!id) throw new Error(`ID missing/blank for ${JSON.stringify(el)}`);
                return id;
            });

            const batchDeleteParams: BatchWriteItemCommandInput = {
                RequestItems: {
                    [tableName]: itemIDs.map((id) => ({
                        DeleteRequest: { Key: { ID: { S: id } } },
                    })),
                },
            };

            await dynamo.send(new BatchWriteItemCommand(batchDeleteParams));
        });
    },
);
