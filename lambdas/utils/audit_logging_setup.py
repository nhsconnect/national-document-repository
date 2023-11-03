import json
import logging

from services.sensitive_audit_service import SensitiveAuditService
from utils.logging_formatter import LoggingFormatter


class LoggingService:
    def __init__(self, name):
        self.name = name

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        self.audit_logger = logging.getLogger("audit")
        self.audit_handler = SensitiveAuditService()
        self.formatter = LoggingFormatter()
        self.audit_handler.setFormatter(self.formatter)
        self.audit_logger.addHandler(self.audit_handler)
        self.audit_logger.setLevel(logging.INFO)

    def audit_splunk_info(self, msg, args: dict = None):
        logging.getLogger("audit.{}".format(self.name))
        message = msg + " " + json.dumps(args)
        self.audit_logger.info(message, extra={"custom_args": args})

    def audit_splunk_error(self, msg, args: dict = None):
        logging.getLogger("audit.{}".format(self.name))
        message = msg + " " + json.dumps(args)
        self.audit_logger.error(message, extra={"custom_args": args})

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)
