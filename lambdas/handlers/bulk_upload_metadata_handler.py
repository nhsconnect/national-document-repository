import csv
import os
import tempfile
from typing import Iterable

import pydantic
from botocore.exceptions import ClientError
from models.staging_metadata import (METADATA_FILENAME, NHS_NUMBER_FIELD_NAME,
                                     MetadataFile, StagingMetadata)
from services.s3_service import S3Service
from services.sqs_service import SQSService
from utils.audit_logging_setup import LoggingService
from utils.decorators.set_audit_arg import set_request_context_for_logging
from utils.decorators.override_error_check import override_error_check

logger = LoggingService(__name__)


@set_request_context_for_logging
@override_error_check
def lambda_handler(_event, _context):
    try:
        logger.info("Starting metadata reading process")

        staging_bucket_name = os.environ["STAGING_STORE_BUCKET_NAME"]
        metadata_queue_url = os.environ["METADATA_SQS_QUEUE_URL"]

        logger.info("Fetching metadata.csv from bucket")
        metadata_file = download_metadata_from_s3(
            staging_bucket_name, METADATA_FILENAME
        )

        logger.info("Parsing bulk upload metadata")
        staging_metadata_list = csv_to_staging_metadata(metadata_file)

        logger.info("Finished parsing metadata")
        send_metadata_to_sqs(staging_metadata_list, metadata_queue_url)

        logger.info("Sent bulk upload metadata to sqs queue")
    except pydantic.ValidationError as e:
        logger.info("Failed to parse metadata.csv")
        logger.error(str(e))
    except KeyError as e:
        logger.info("Failed due to missing key")
        logger.error(str(e))
    except ClientError as e:
        logger.error(str(e))
        if "HeadObject" in str(e):
            logger.error(
                f'No metadata file could be found with the name "{METADATA_FILENAME}"'
            )


def download_metadata_from_s3(staging_bucket_name: str, metadata_filename: str):
    s3_service = S3Service()
    temp_dir = tempfile.mkdtemp()

    local_file_path = os.path.join(temp_dir, metadata_filename)
    s3_service.download_file(
        s3_bucket_name=staging_bucket_name,
        file_key=metadata_filename,
        download_path=local_file_path,
    )
    return local_file_path


def csv_to_staging_metadata(csv_file_path: str) -> list[StagingMetadata]:
    patients = {}
    with open(csv_file_path, mode="r") as csv_file_handler:
        csv_reader: Iterable[dict] = csv.DictReader(csv_file_handler)
        for row in csv_reader:
            file_metadata = MetadataFile.model_validate(row)
            nhs_number = row[NHS_NUMBER_FIELD_NAME]
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
        logger.info(f"Sending metadata for patientId: {nhs_number}")

        sqs_service.send_message_with_nhs_number_attr(
            queue_url=metadata_queue_url,
            message_body=staging_metadata.model_dump_json(by_alias=True),
            nhs_number=nhs_number,
        )
