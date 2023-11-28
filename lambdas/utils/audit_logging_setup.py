import logging

from services.sensitive_audit_service import SensitiveAuditService
from utils.logging_formatter import LoggingFormatter


class LoggingService:
    audit_logger = None

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.configure_audit_logger()
        self.formatter = LoggingFormatter()
        logging.Formatter.format = self.formatter.format

    def configure_audit_logger(self):
        if self.__class__.audit_logger is None:
            self.__class__.audit_logger = logging.getLogger("audit")
            audit_handler = SensitiveAuditService()
            self.__class__.audit_logger.addHandler(audit_handler)
            self.__class__.audit_logger.setLevel(logging.INFO)

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
