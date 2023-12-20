import os
import uuid

from models.staging_metadata import StagingMetadata
from services.sqs_service import SQSService
from utils.audit_logging_setup import LoggingService
from utils.request_context import request_context

_logger = LoggingService(__name__)


class BulkUploadSqsRepository:
    def __init__(self):
        self.sqs_repository = SQSService()
        self.invalid_queue_url = os.environ["INVALID_SQS_QUEUE_URL"]
        self.metadata_queue_url = os.environ["METADATA_SQS_QUEUE_URL"]

    def put_staging_metadata_back_to_queue(self, staging_metadata: StagingMetadata):
        request_context.patient_nhs_no = staging_metadata.nhs_number
        setattr(staging_metadata, "retries", (staging_metadata.retries + 1))
        _logger.info("Returning message to sqs queue...")
        self.sqs_repository.send_message_with_nhs_number_attr_fifo(
            queue_url=self.metadata_queue_url,
            message_body=staging_metadata.model_dump_json(by_alias=True),
            nhs_number=staging_metadata.nhs_number,
            group_id=f"back_to_queue_bulk_upload_{uuid.uuid4()}",
        )

    def put_sqs_message_back_to_queue(self, sqs_message: dict):
        try:
            nhs_number = sqs_message["messageAttributes"]["NhsNumber"]["stringValue"]
            request_context.patient_nhs_no = nhs_number
        except KeyError:
            nhs_number = ""

        _logger.info("Returning message to sqs queue...")
        self.sqs_repository.send_message_with_nhs_number_attr_fifo(
            queue_url=self.metadata_queue_url,
            message_body=sqs_message["body"],
            nhs_number=nhs_number,
        )
