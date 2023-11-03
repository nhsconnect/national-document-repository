import json
import os
from logging import StreamHandler

from services.sqs_service import SQSService


class SensitiveAuditService(SQSService, StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.splunk_sqs_queue = os.getenv("SPLUNK_SQS_QUEUE_URL")

    def emit(self, record):
        if self.splunk_sqs_queue:
            self.send_message(
                queue_url=self.splunk_sqs_queue, message_body=self.format(record)
            )
