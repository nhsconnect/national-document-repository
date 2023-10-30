import os

from services.sqs_service import SQSService
from utils.exceptions import MissingEnvVarException


class SensitiveAuditService(SQSService):
    def __init__(self):
        super().__init__()
        try:
            self.splunk_sqs_queue = os.environ["SPLUNK_SQS_QUEUE_URL"]
        except KeyError:
            raise MissingEnvVarException("Failed to initialise Splunk Service")

    def publish(self, message: str):
        self.send_message(queue_url=self.splunk_sqs_queue, message_body=message)
