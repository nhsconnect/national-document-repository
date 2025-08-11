// cypress/support/commands.d.ts
/// <reference types="cypress" />

import type { PutObjectCommandOutput, DeleteObjectCommandOutput } from '@aws-sdk/client-s3';
import type {
    PutItemCommandOutput,
    DeleteItemCommandOutput,
    BatchWriteItemCommandOutput,
} from '@aws-sdk/client-dynamodb';

declare global {
    namespace Cypress {
        interface Chainable {
            addPdfFileToS3(
                bucketName: string,
                fileName: string,
                filePath: string,
            ): Chainable<PutObjectCommandOutput>;

            addItemToDynamoDb(
                tableName: string,
                item: Record<string, unknown>,
            ): Chainable<PutItemCommandOutput>;

            deleteFileFromS3(
                bucketName: string,
                fileName: string,
            ): Chainable<DeleteObjectCommandOutput>;

            deleteItemFromDynamoDb(
                tableName: string,
                itemId: string,
            ): Chainable<DeleteItemCommandOutput>;

            // This command first queries, then batch-deletes; you return void when nothing to delete.
            deleteItemsBySecondaryKeyFromDynamoDb(
                tableName: string,
                index: string,
                attribute: string,
                value: string,
            ): Chainable<void>;
        }
    }
}

export {};
