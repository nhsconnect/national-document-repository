import csv
import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

from models.staging_metadata import MetadataFile, StagingMetadata

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        logger.info("Starting metadata reading process")

        staging_bucket_name = os.environ["STAGING_STORE_BUCKET_NAME"]
        metadata_queue_url = os.environ["METADATA_SQS_QUEUE_URL"]

        s3_client = boto3.client("s3")

        logger.info("Reading metadata.csv from bucket")
        s3_response = s3_client.get_object(
            Bucket=staging_bucket_name, Key="metadata.csv"
        )
        csv_content = s3_response["Body"].read().split(b"\n")
        staging_metadata_list = csv_to_staging_metadata(csv_content)

        sqs_client = boto3.client("sqs")

        for staging_metadata in staging_metadata_list:
            nhs_number = staging_metadata.nhs_number
            sqs_client.send_message(
                QueueUrl=metadata_queue_url,
                DelaySeconds=10,
                MessageAttributes={
                    "NhsNumber": {"DataType": "String", "StringValue": str(nhs_number)},
                },
                MessageBody=json.dumps(staging_metadata),
            )
    except KeyError as e:
        logger.info("Failed due to missing key")
        logger.error(str(e))
    except ClientError as e:
        logger.error(str(e))


def csv_to_staging_metadata(csv_content) -> list[StagingMetadata]:
    results = {}
    csv_reader = csv.DictReader(csv_content)

    for row in csv_reader:
        file_metadata = MetadataFile.model_validate(row)
        nhs_number = row["nhs_number"]
        if nhs_number not in results:
            results[nhs_number] = [file_metadata]
        else:
            results[nhs_number] += [file_metadata]

    return [
        StagingMetadata(nhs_number=nhs_number, files=results[nhs_number])
        for nhs_number in results
    ]
