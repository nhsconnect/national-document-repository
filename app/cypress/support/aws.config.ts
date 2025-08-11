// cypress/support/commands.d.ts
/// <reference types="cypress" />

import { S3Client } from '@aws-sdk/client-s3';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

import type { AwsCredentialIdentity } from '@aws-sdk/types';

const env = (k: string): string => {
    const v = Cypress.env(k);
    if (!v) throw new Error(`Missing ${k} in Cypress.env`);
    return String(v);
};

const region = env('AWS_REGION');

const credentials: AwsCredentialIdentity = {
    accessKeyId: env('AWS_ACCESS_KEY_ID'),
    secretAccessKey: env('AWS_SECRET_ACCESS_KEY'),
    sessionToken: Cypress.env('AWS_SESSION_TOKEN')
        ? String(Cypress.env('AWS_SESSION_TOKEN'))
        : undefined,
};

export const s3 = new S3Client({ region, credentials });
export const dynamo = new DynamoDBClient({ region, credentials });

const awsClients = { s3, dynamo };
export default awsClients;
