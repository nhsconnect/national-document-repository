import os
import uuid
from logging import StreamHandler

from services.sqs_service import SQSService


class SensitiveAuditService(StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.splunk_sqs_queue = os.getenv("SPLUNK_SQS_QUEUE_URL")
        self.sqs_client = None

    def emit(self, record):
        sqs_group_id = f"splunk_{uuid.uuid4()}"

        if self.splunk_sqs_queue:
            if self.sqs_client is None:
                self.sqs_client = SQSService()
            self.sqs_client.send_message_fifo(
                queue_url=self.splunk_sqs_queue,
                message_body=self.format(record),
                group_id=sqs_group_id,
            )
