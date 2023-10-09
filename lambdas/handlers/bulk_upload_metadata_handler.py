import csv
import logging
import os
import tempfile
from typing import Iterable

import pydantic
from botocore.exceptions import ClientError
from models.staging_metadata import (METADATA_FILENAME, MetadataFile,
                                     StagingMetadata)
from services.s3_service import S3Service
from services.sqs_service import SQSService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(_event, _context):
    # This lambda is supposed to be trigger manually / by S3 upload, and the output is sent to sqs queue,
    # so we don't return any response
    try:
        logger.info("Starting metadata reading process")

        staging_bucket_name = os.environ["STAGING_STORE_BUCKET_NAME"]
        metadata_queue_url = os.environ["METADATA_SQS_QUEUE_URL"]

        metadata_file = download_metadata_from_s3(
            staging_bucket_name, METADATA_FILENAME
        )

        staging_metadata_list = csv_to_staging_metadata(metadata_file)

        send_metadata_to_sqs(staging_metadata_list, metadata_queue_url)
    except pydantic.ValidationError as e:
        logger.info("Failed to parse metadata.csv")
        logger.error(str(e))
    except KeyError as e:
        logger.info("Failed due to missing key")
        logger.error(str(e))
    except ClientError as e:
        logger.error(str(e))


def download_metadata_from_s3(staging_bucket_name: str, metadata_filename: str):
    s3_service = S3Service()
    temp_dir = tempfile.mkdtemp()
    logger.info("Fetching metadata.csv from bucket")
    local_file_path = os.path.join(temp_dir, metadata_filename)
    s3_service.download_file(
        s3_bucket_name=staging_bucket_name,
        file_key=metadata_filename,
        download_path=local_file_path,
    )
    return local_file_path


def csv_to_staging_metadata(csv_file_path: str) -> list[StagingMetadata]:
    patients = {}
    nhs_number_field_key = "nhs_number"  # TODO: refer this from model definition
    with open(csv_file_path, mode="r") as csv_file_handler:
        csv_reader: Iterable[dict] = csv.DictReader(csv_file_handler)
        for row in csv_reader:
            file_metadata = MetadataFile.model_validate(row)
            nhs_number = row[nhs_number_field_key]
            if nhs_number not in patients:
                patients[nhs_number] = [file_metadata]
            else:
                patients[nhs_number] += [file_metadata]

    return [
        StagingMetadata(nhs_number=nhs_number, files=patients[nhs_number])
        for nhs_number in patients
    ]


def send_metadata_to_sqs(
    staging_metadata_list: list[StagingMetadata], metadata_queue_url: str
) -> None:
    sqs_service = SQSService()

    for staging_metadata in staging_metadata_list:
        nhs_number = staging_metadata.nhs_number
        sqs_service.send_message_with_nhs_number_attr(
            queue_url=metadata_queue_url,
            message_body=staging_metadata.model_dump_json(),
            nhs_number=str(nhs_number),
        )
