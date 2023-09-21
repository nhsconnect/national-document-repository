import logging

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    table = boto3.resource('dynamodb').Table('ndr-dev_DocumentReferenceMetadata')
    file_location = "s3://ndr-dev-document-store/9ccfb094-c029-42c2-a432-a8346e5a3ee1"
    file_id = "9ccfb094-c029-42c2-a432-a8346e5a3ee1"
    nhs_number = "1111111111"

    try:
        return table.update_item(
            Key={'ID': "9ccfb094-c029-42c2-a432-a8346e5a3ee1"},
            UpdateExpression="set VirusScannerResult = :r",
            ExpressionAttributeValues={
                ':r': 'Clean',
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        logging.error(e)
        return False
