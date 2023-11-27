import os
from logging import StreamHandler

from services.sqs_service import SQSService


class SensitiveAuditService(StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.splunk_sqs_queue = os.getenv("SPLUNK_SQS_QUEUE_URL")
        self.sqs_client = None

    def emit(self, record):
        if self.splunk_sqs_queue:
            if self.sqs_client is None:
                self.sqs_client = SQSService()
            self.sqs_client.send_message_standard(
                queue_url=self.splunk_sqs_queue,
                message_body=self.format(record),
            )
