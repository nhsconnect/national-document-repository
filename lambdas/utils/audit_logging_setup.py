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
        logging.Formatter.format = self.formatter.format

        self.audit_logger.addHandler(self.audit_handler)
        self.audit_logger.setLevel(logging.INFO)

    def audit_splunk_info(self, msg, args: dict = None):
        logging.getLogger("audit.{}".format(self.name))
        self.audit_logger.info(msg, extra={"custom_args": args})

    def audit_splunk_error(self, msg, custom_args: dict = None, **kwargs):
        logging.getLogger("audit.{}".format(self.name))
        self.audit_logger.error(msg, extra={"custom_args": custom_args})

    def info(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.info(message, extra={"custom_args": custom_args}, *args, **kwargs)

    def error(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.error(message, extra={"custom_args": custom_args}, *args, **kwargs)

    def warning(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.warning(
            message, extra={"custom_args": custom_args}, *args, **kwargs
        )

    def debug(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.debug(message, extra={"custom_args": custom_args}, *args, **kwargs)

    def exception(
        self, message, custom_args: dict = None, *args, exc_info=True, **kwargs
    ):
        self.logger.exception(
            message, exc_info, extra={"custom_args": custom_args}, *args, **kwargs
        )

    def critical(self, message, custom_args: dict = None, *args, **kwargs):
        self.logger.critical(
            message, extra={"custom_args": custom_args}, *args, **kwargs
        )
