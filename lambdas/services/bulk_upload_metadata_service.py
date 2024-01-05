import csv
import os
import shutil
import tempfile
import uuid
from typing import Iterable

import pydantic
from botocore.exceptions import ClientError
from models.staging_metadata import NHS_NUMBER_FIELD_NAME, MetadataFile, StagingMetadata
from services.base.s3_service import S3Service
from services.base.sqs_service import SQSService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class BulkUploadMetadataService:
    def __init__(self):
        self.s3_service = S3Service()
        self.sqs_service = SQSService()

        self.staging_bucket_name = os.environ["STAGING_STORE_BUCKET_NAME"]
        self.metadata_queue_url = os.environ["METADATA_SQS_QUEUE_URL"]

        self.temp_download_dir = tempfile.mkdtemp()

    def process_metadata(self, metadata_filename: str):
        try:
            logger.info("Fetching metadata.csv from bucket")
            metadata_file = self.download_metadata_from_s3(metadata_filename)

            logger.info("Parsing bulk upload metadata")
            staging_metadata_list = self.csv_to_staging_metadata(metadata_file)

            logger.info("Finished parsing metadata")
            self.send_metadata_to_fifo_sqs(staging_metadata_list)

            logger.info("Sent bulk upload metadata to sqs queue")

            self.clear_temp_storage()

        except pydantic.ValidationError as e:
            logger.info(
                "Failed to parse metadata.csv", {"Result": "Unsuccessful bulk upload"}
            )
            logger.error(str(e))
        except KeyError as e:
            logger.info(
                "Failed due to missing key", {"Result": "Unsuccessful bulk upload"}
            )
            logger.error(str(e))
        except ClientError as e:
            logger.error(str(e))
            if "HeadObject" in str(e):
                logger.error(
                    f'No metadata file could be found with the name "{metadata_filename}"',
                    {"Result": "Unsuccessful bulk upload"},
                )

    def download_metadata_from_s3(self, metadata_filename: str) -> str:
        local_file_path = os.path.join(self.temp_download_dir, metadata_filename)
        self.s3_service.download_file(
            s3_bucket_name=self.staging_bucket_name,
            file_key=metadata_filename,
            download_path=local_file_path,
        )
        return local_file_path

    @staticmethod
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

    def send_metadata_to_fifo_sqs(
        self, staging_metadata_list: list[StagingMetadata]
    ) -> None:
        sqs_group_id = f"bulk_upload_{uuid.uuid4()}"

        for staging_metadata in staging_metadata_list:
            nhs_number = staging_metadata.nhs_number
            logger.info(f"Sending metadata for patientId: {nhs_number}")

            self.sqs_service.send_message_with_nhs_number_attr_fifo(
                queue_url=self.metadata_queue_url,
                message_body=staging_metadata.model_dump_json(by_alias=True),
                nhs_number=nhs_number,
                group_id=sqs_group_id,
            )

    def clear_temp_storage(self):
        shutil.rmtree(self.temp_download_dir)
